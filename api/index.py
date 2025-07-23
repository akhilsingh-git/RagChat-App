import os
import requests
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

# Load environment variables (for the EC2_INFERENCE_SERVER_URL)
load_dotenv()

app = FastAPI(title="RAG System API Proxy")

# Get the URL of your EC2 server from an environment variable
EC2_URL = os.getenv("EC2_INFERENCE_SERVER_URL")

@app.get("/api/query")
def query_proxy(request: Request):
    """
    This function acts as a proxy. It receives a request from the user's browser,
    forwards it to the powerful EC2 server, and streams the response back.
    """
    if not EC2_URL:
        # This error will be streamed back to the user if the env var is missing
        async def error_stream():
            yield "data: Error: The inference server is not configured on Vercel.\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    # Get the user's query from the request
    query = request.query_params.get('query', '')
    
    # Construct the full URL for the EC2 server's API endpoint
    inference_url = f"{EC2_URL}/api/query?query={query}"

    try:
        # Make a streaming request to the EC2 server
        # The 'stream=True' is critical here
        response = requests.get(inference_url, stream=True, timeout=30)
        response.raise_for_status() # Raise an error for bad status codes
        
        # Stream the response from the EC2 server back to the client
        return StreamingResponse(response.iter_content(chunk_size=1024), media_type="text/event-stream")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to inference server: {e}")
        async def error_stream():
            yield f"data: Error: Could not connect to the AI service. Please check the EC2 server.\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")


# --- Static files mounting remains the same ---
# This serves your index.html and script.js
static_files_dir = os.path.join(os.path.dirname(__file__), "..", "public")
app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
