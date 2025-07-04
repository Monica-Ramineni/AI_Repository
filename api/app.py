# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
from typing import Optional, List
import uuid
import asyncio

# Import Pydantic for data validation and settings management
from pydantic import BaseModel

# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI

# Import aimakerspace components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.embedding import EmbeddingModel

# Initialize FastAPI application with a title
app = FastAPI(title="RAG Chat API with PDF Support using AIMakerSpace")

# Configure CORS (Cross-Origin Resource Sharing) middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store vector databases for different sessions
vector_dbs = {}

# Define the data models using Pydantic
class ChatRequest(BaseModel):
    developer_message: str
    user_message: str
    model: Optional[str] = "gpt-4.1-mini"
    api_key: str
    session_id: Optional[str] = None
    use_rag: Optional[bool] = False

class UploadResponse(BaseModel):
    message: str
    session_id: str
    filename: str
    chunks_count: int

def save_uploaded_file(upload_file: UploadFile) -> str:
    """Save uploaded file to temporary location and return path."""
    try:
        # Create temporary file
        suffix = os.path.splitext(upload_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            shutil.copyfileobj(upload_file.file, tmp_file)
            tmp_path = tmp_file.name
        
        return tmp_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

def process_pdf_with_aimakerspace(file_path: str, session_id: str) -> int:
    """Process PDF using aimakerspace library and return number of chunks."""
    try:
        # Load PDF using aimakerspace
        pdf_loader = PDFLoader(file_path)
        documents = pdf_loader.load_documents()
        
        if not documents or not documents[0].strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF")
        
        # Split text into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_texts(documents)
        
        if not chunks:
            return 0
        
        # Create vector database for session
        embedding_model = EmbeddingModel()
        vector_db = VectorDatabase(embedding_model)
        
        # Build vector database from chunks
        asyncio.run(vector_db.abuild_from_list(chunks))
        
        # Store vector database for session
        vector_dbs[session_id] = vector_db
        
        return len(chunks)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except:
            pass

@app.post("/api/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """Upload and process a PDF file for RAG functionality using aimakerspace."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        file_path = save_uploaded_file(file)
        
        # Process PDF using aimakerspace
        chunks_count = process_pdf_with_aimakerspace(file_path, session_id)
        
        return UploadResponse(
            message="PDF uploaded and processed successfully using AIMakerSpace",
            session_id=session_id,
            filename=file.filename,
            chunks_count=chunks_count
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{session_id}")
async def get_documents(session_id: str):
    """Get information about uploaded documents for a session."""
    try:
        if session_id not in vector_dbs:
            return {
                "session_id": session_id,
                "total_chunks": 0,
                "documents": []
            }
        
        vector_db = vector_dbs[session_id]
        total_chunks = len(vector_db.vectors)
        
        return {
            "session_id": session_id,
            "total_chunks": total_chunks,
            "documents": ["PDF Document"]  # Since we don't store filenames separately
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{session_id}")
async def clear_documents(session_id: str):
    """Clear all documents for a session."""
    try:
        if session_id in vector_dbs:
            del vector_dbs[session_id]
        return {"message": f"Documents cleared for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with RAG support using aimakerspace."""
    try:
        client = OpenAI(api_key=request.api_key)
        
        # Prepare context from RAG if enabled
        context = ""
        if request.use_rag and request.session_id and request.session_id in vector_dbs:
            vector_db = vector_dbs[request.session_id]
            
            # Search for relevant chunks
            relevant_texts = vector_db.search_by_text(
                request.user_message, 
                k=3, 
                return_as_text=True
            )
            
            if relevant_texts:
                context = "\n\nRelevant document information:\n" + "\n".join(relevant_texts)
        
        # Create system message with context
        system_message = request.developer_message
        if context:
            system_message += f"\n\n{context}\n\nWhen answering, use the provided document information when relevant. If the document information doesn't contain relevant details for the question, answer based on your general knowledge."
        
        async def generate():
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "features": ["chat", "pdf_upload", "rag", "aimakerspace"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
