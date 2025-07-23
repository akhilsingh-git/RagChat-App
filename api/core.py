import os
import json
import requests
from sqlalchemy.orm import Session
from . import crud

# --- Configuration ---
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
HUGGING_FACE_HEADERS = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}
EMBEDDING_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/TaylorAI/bge-micro"
GENERATOR_API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def run_rag_pipeline(db: Session, query: str, k: int = 3):
    """
    A generator function that performs the entire RAG pipeline and streams updates.
    This architecture prevents the Netlify function from timing out.
    """
    try:
        # --- Step 1: Get Query Embedding ---
        yield 'data: {"status": "Embedding query..."}\n\n'
        response = requests.post(EMBEDDING_API_URL, headers=HUGGING_FACE_HEADERS, json={"inputs": query, "options": {"wait_for_model": True}})
        response.raise_for_status()
        query_embedding = response.json()

        # --- Step 2: Search Database ---
        yield 'data: {"status": "Searching database..."}\n\n'
        retrieved_docs = crud.get_top_k_documents(db, query_embedding, k)
        if not retrieved_docs:
            yield 'data: {"status": "No relevant documents found."}\n\n'
            yield 'data: {"done": true}\n\n'
            return

        # --- Step 3: Generate Final Answer ---
        yield 'data: {"status": "Generating answer..."}\n\n'
        context = "\n---\n".join([doc.text_content for doc in retrieved_docs])
        
        prompt = f"System: You are a helpful AI assistant. Answer the user's question based only on the provided context.\nUser: CONTEXT:\n{context}\n\nQUESTION:\n{query}\nAssistant:"
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.1}, "stream": True}
        
        with requests.post(GENERATOR_API_URL, headers=HUGGING_FACE_HEADERS, json=payload, stream=True) as gen_response:
            gen_response.raise_for_status()
            for line in gen_response.iter_lines():
                if line:
                    try:
                        # The HF streaming response is "data: {...}"
                        line_str = line.decode('utf-8')
                        if line_str.startswith("data:"):
                            data = json.loads(line_str.replace("data:", ""))
                            token = data.get("token", {}).get("text", "")
                            # Stream the actual token
                            yield f'data: {json.dumps({"token": token})}\n\n'
                    except json.JSONDecodeError:
                        continue
        
        # --- Step 4: Signal Completion ---
        yield 'data: {"done": true}\n\n'

    except Exception as e:
        error_message = str(e)
        yield f'data: {json.dumps({"error": error_message})}\n\n'
        yield 'data: {"done": true}\n\n'
