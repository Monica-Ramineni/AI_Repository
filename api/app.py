print("app.py starting up")

# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
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
from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter, TextFileLoader, DocxFileLoader
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

# Store vector databases and document metadata for different sessions
vector_dbs = {}
document_metadata = {}  # session_id -> list of {filename, filetype, chunks_count}

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
    """Save uploaded file to /tmp and return path (Vercel compatibility)."""
    try:
        # Always use /tmp for temp files (Vercel's writable directory)
        suffix = os.path.splitext(upload_file.filename)[1]
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=tmp_dir) as tmp_file:
            shutil.copyfileobj(upload_file.file, tmp_file)
            tmp_path = tmp_file.name
        return tmp_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

async def process_document_with_aimakerspace_async(file_path: str, session_id: str, filetype: str) -> int:
    """Process document using aimakerspace library and return number of chunks (async version)."""
    try:
        if filetype == 'pdf':
            loader = PDFLoader(file_path)
        elif filetype == 'docx':
            loader = DocxFileLoader(file_path)
        elif filetype == 'txt':
            loader = TextFileLoader(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        documents = loader.load_documents()
        if not documents or not documents[0].strip():
            raise HTTPException(status_code=400, detail="No text content found in document")
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_texts(documents)
        if not chunks:
            return 0
        embedding_model = EmbeddingModel()
        vector_db = VectorDatabase(embedding_model)
        await vector_db.abuild_from_list(chunks)
        # Store or update vector database for session
        if session_id not in vector_dbs:
            vector_dbs[session_id] = vector_db
        else:
            # Optionally, merge or replace as needed
            vector_dbs[session_id] = vector_db
        # Store document metadata
        if session_id not in document_metadata:
            document_metadata[session_id] = []
        document_metadata[session_id].append({
            'filename': os.path.basename(file_path),
            'filetype': filetype,
            'chunks_count': len(chunks)
        })
        return len(chunks)
    except Exception as e:
        print(f"process_document_with_aimakerspace_async error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        try:
            os.unlink(file_path)
        except:
            pass

@app.post("/api/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """Upload and process a document (PDF, DOCX, TXT) for RAG functionality using aimakerspace."""
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        filetype = 'pdf'
    elif filename.endswith('.docx'):
        filetype = 'docx'
    elif filename.endswith('.txt'):
        filetype = 'txt'
    else:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")
    if not session_id:
        session_id = str(uuid.uuid4())
    try:
        file_path = save_uploaded_file(file)
        chunks_count = await process_document_with_aimakerspace_async(file_path, session_id, filetype)
        return {
            "message": f"{filetype.upper()} uploaded and processed successfully using AIMakerSpace",
            "session_id": session_id,
            "filename": file.filename,
            "filetype": filetype,
            "chunks_count": chunks_count,
            "documents": document_metadata.get(session_id, [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{session_id}")
async def get_documents(session_id: str):
    """Get information about uploaded documents for a session."""
    try:
        docs = document_metadata.get(session_id, [])
        total_chunks = sum(doc['chunks_count'] for doc in docs)
        return {
            "session_id": session_id,
            "total_chunks": total_chunks,
            "documents": docs
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

@app.post("/api/summarize")
async def summarize_document(
    session_id: str = Body(...),
    filename: str = Body(...),
    filetype: str = Body(...),
    api_key: Optional[str] = Body(None)
):
    """Summarize a document for a session using OpenAI."""
    try:
        # Find the document in metadata
        docs = document_metadata.get(session_id, [])
        doc_meta = next((d for d in docs if d['filename'] == filename and d['filetype'] == filetype), None)
        if not doc_meta:
            raise HTTPException(status_code=404, detail="Document not found for session")
        # Retrieve the text from the vector DB (use all chunks)
        vector_db = vector_dbs.get(session_id)
        if not vector_db:
            raise HTTPException(status_code=404, detail="No vector DB for session")
        # For simplicity, concatenate all chunk keys (which are the text chunks)
        all_text = "\n".join(list(vector_db.vectors.keys()))
        if not all_text.strip():
            raise HTTPException(status_code=400, detail="No text found in document")
        # Use OpenAI to summarize
        client = OpenAI(api_key=api_key) if api_key else OpenAI()
        prompt = f"Summarize the following legal document for a legal professional. Focus on key points, obligations, and important sections.\n\n{all_text[:12000]}"  # Limit to 12k chars for safety
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = completion.choices[0].message.content.strip()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing document: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "features": ["chat", "pdf_upload", "rag", "aimakerspace"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
