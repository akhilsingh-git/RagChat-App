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

from .core import RAGService, get_rag_service
from .database import get_db
from .logging_config import setup_logging

# --- Setup Logging and Metrics ---
setup_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(title="RAG System API")

# Instrument the app with Prometheus metrics
Instrumentator().instrument(app).expose(app)

# --- Middleware for Structured Logging ---
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.perf_counter()
    
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client_host=request.client.host,
    )

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    logger.info(
        "request_finished",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=round(process_time, 4),
    )
    
    return response

# --- API Endpoints ---
@app.get("/api/query")
def query_system_stream(
    request: Request,
    rag_service: RAGService = Depends(get_rag_service),
    db: Session = Depends(get_db)
):
    query = request.query_params.get('query', '')
    k = int(request.query_params.get('k', 3))

    if not query:
        logger.warning("empty_query_received")
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")
    
    logger.info("streaming_query_received", query=query)
    return StreamingResponse(
        rag_service.generate_answer_stream(db, query, k),
        media_type="text/event-stream"
    )

# --- Static files mounting remains the same ---
static_files_dir = os.path.join(os.path.dirname(__file__), "..", "public")
app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")