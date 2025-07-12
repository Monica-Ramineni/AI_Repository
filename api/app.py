from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from Bio import Entrez
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- FastAPI Setup ---
app = FastAPI(
    title="Health Chat Agent",
    description="A full-stack health assistant with web search, PubMed research, and symptom checking capabilities",
    version="1.0.0"
)

# Allow all CORS (since frontend is hosted separately)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tool 1: Tavily Web Search
tavily_tool = TavilySearch(max_results=3)

# Tool 2: PubMed Search
def pubmed_search(query):
    Entrez.email = "your@email.com"
    handle = Entrez.esearch(db="pubmed", term=query, retmax=3)
    record = Entrez.read(handle)
    ids = record["IdList"]
    if not ids:
        return "No PubMed articles found."
    summaries = []
    for pmid in ids:
        summary_handle = Entrez.esummary(db="pubmed", id=pmid)
        summary = Entrez.read(summary_handle)
        summaries.append(summary[0]["Title"])
    return "\n".join(summaries)

# Tool 3: Symptom Checker
def symptom_checker(symptoms):
    symptom_map = {
        "fever": "Possible conditions: flu, COVID-19, infection.",
        "headache": "Possible conditions: migraine, tension headache, dehydration.",
        "cough": "Possible conditions: cold, flu, bronchitis."
    }
    results = []
    for symptom in symptoms.split(","):
        symptom = symptom.strip().lower()
        if symptom in symptom_map:
            results.append(symptom_map[symptom])
    return "\n".join(results) if results else "No suggestions found."

# Decision-making agent
def agent(query):
    q = query.lower().strip()
    if "pubmed" in q:
        search_term = q.replace("pubmed", "").strip()
        return pubmed_search(search_term), "pubmed"
    elif "symptom" in q:
        symptoms = q.replace("symptom", "").strip()
        return symptom_checker(symptoms), "symptom"
    elif q in ["hello", "hi", "hey"] or any(q.startswith(greet + " ") for greet in ["hello", "hi", "hey"]):
        return "Hello! How can I help you with your health questions today?", "greeting"
    else:
        return tavily_tool.invoke({"query": query}), "tavily"

# Request model
class Query(BaseModel):
    question: str

# Endpoint
@app.post("/ask")
async def ask(query: Query):
    answer, typ = agent(query.question)
    return {"type": typ, "data": answer}

# Health check (optional but useful)
@app.get("/health")
def health_check():
    return {"status": "ok"}
