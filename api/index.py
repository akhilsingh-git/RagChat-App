import os
import json
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from mangum import Mangum

# Import the new core logic and database session manager
from .core import run_rag_pipeline
from .database import get_db

app = FastAPI(title="Netlify RAG API")

@app.get("/api/query")
def query_stream(request: Request, db: Session = Depends(get_db)):
    """
    Main API endpoint that streams the RAG process.
    """
    query = request.query_params.get('query', '')
    if not query:
        async def error_stream():
            yield 'data: {"error": "Query parameter is missing."}\n\n'
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    # The run_rag_pipeline function is a generator that does all the work
    return StreamingResponse(run_rag_pipeline(db, query), media_type="text/event-stream")

# Mount the static frontend files
static_files_dir = os.path.join(os.path.dirname(__file__), "..", "public")
app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")

# Create the handler that AWS Lambda will invoke
handler = Mangum(app)
