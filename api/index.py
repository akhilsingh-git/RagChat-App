import os
import time
import uuid
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
import structlog
import numpy as np

from .core import RAGService, get_rag_service
from .database import get_db
from .logging_config import setup_logging
from . import crud, models # Import crud and models

# --- Setup Logging and Metrics ---
setup_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(title="RAG System API")
Instrumentator().instrument(app).expose(app)

# --- Middleware for Structured Logging ---
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)
    start_time = time.perf_counter()
    logger.info("request_started", method=request.method, path=request.url.path)
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info("request_finished", status_code=response.status_code, process_time=round(process_time, 4))
    return response

# --- Pydantic Models for new endpoints ---
class DocumentInsertRequest(BaseModel):
    id: str
    text: str

class SearchRequest(BaseModel):
    query: str
    k: int = 3

class SearchResult(BaseModel):
    id: str
    text: str
    # Note: We don't expose the embedding vector itself
    
class SearchResponse(BaseModel):
    results: List[SearchResult]

# --- API Endpoints ---

@app.get("/api/query")
def query_system_stream(
    request: Request,
    rag_service: RAGService = Depends(get_rag_service),
    db: Session = Depends(get_db)
):
    query = request.query_params.get('query', '')
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")
    logger.info("streaming_query_received", query=query)
    return StreamingResponse(
        rag_service.generate_answer_stream(db, query),
        media_type="text/event-stream"
    )

@app.post("/api/insert", status_code=201, summary="Insert a single document")
def insert_document(
    doc: DocumentInsertRequest,
    rag_service: RAGService = Depends(get_rag_service),
    db: Session = Depends(get_db)
):
    """
    Receives a single document, generates its embedding, and inserts it into the database.
    """
    try:
        logger.info("insert_request_received", doc_id=doc.id)
        embedding = rag_service.embedding_model.encode(doc.text)
        crud.create_document(db, doc_id=doc.id, text=doc.text, embedding=embedding)
        return {"status": "success", "id": doc.id}
    except Exception as e:
        logger.error("insert_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to insert document.")

@app.post("/api/search", response_model=SearchResponse, summary="Search for documents")
def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service),
    db: Session = Depends(get_db)
):
    """
    Receives a query, generates its embedding, and returns the top-k most similar documents.
    """
    try:
        logger.info("search_request_received", query=request.query)
        query_embedding = rag_service.embedding_model.encode(request.query)
        
        # Using the existing CRUD function for the search
        retrieved_docs = crud.get_top_k_documents(db, query_embedding, request.k)
        
        # Format the results into the Pydantic model
        results = [SearchResult(id=doc.id, text=doc.text_content) for doc in retrieved_docs]
        return SearchResponse(results=results)
        
    except Exception as e:
        logger.error("search_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to perform search.")


# --- Static files mounting remains the same ---
static_files_dir = os.path.join(os.path.dirname(__file__), "..", "public")
app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
