Production-Ready RAG System
This project is a complete Retrieval-Augmented Generation (RAG) system built to demonstrate a full software development lifecycle, from custom component implementation to automated cloud deployment.

What Was Done
1. Custom Vector Database
An in-memory vector database was built from scratch using Python and NumPy.

It supports single and batch insertions of document embeddings.

The search operation uses dot product similarity to retrieve the top-k most relevant documents for a given query.

The implementation uses a simple but effective "flat index" for exact similarity search.

2. RAG Components
Text Embeddings: The TaylorAI/bge-micro model is used via the sentence-transformers library to generate vector embeddings for documents and queries.

Text Generation: The gpt2 model is used via the transformers library to generate human-like answers based on the context retrieved from the vector database.

Data Source: The system loads its knowledge base from the provided documents.json file on startup.

3. Web Application
A complete web application was created using the FastAPI framework.

A clean, responsive chat interface was built with vanilla HTML, Tailwind CSS, and JavaScript, allowing users to interact with the system.

The backend exposes a /api/query endpoint that handles the entire RAG pipeline: embedding the user's query, searching the database, and generating a final answer.

4. Development Environment
Local Development: The application is configured to run locally with a single command (uvicorn api.index:app --reload). The local server serves both the backend API and the static frontend files.

Containerization: The application is fully containerized using Docker, allowing for consistent and portable deployments. A production-ready gunicorn server is used inside the container.

How to Run
Local Development (without Docker)
Install dependencies:

pip install -r requirements.txt

Run the server:

uvicorn api.index:app --reload

Open your browser to http://127.0.0.1:8000.

Running with Docker
Build the Docker image:

docker build -t rag-app .

Run the Docker container:

docker run -p 8000:8000 rag-app

Open your browser to http://127.0.0.1:8000.

What More Would I Do With More Time?
The current implementation is a robust prototype. To make it truly production-grade and scalable, I would focus on the following enhancements:

1. Persistent & Scalable Vector Database
Problem: The current in-memory database does not persist data between server restarts and cannot scale to millions of documents.

Solution: I would replace the custom NumPy database with a production-ready vector database solution like PostgreSQL with the pgvector extension. This provides data persistence, transactional integrity, and the ability to leverage existing database management tools.

2. Approximate Nearest Neighbor (ANN) Search
Problem: The current "flat index" performs an exhaustive search, which becomes slow with a large number of vectors.

Solution: I would implement an ANN index, such as HNSW (Hierarchical Navigable Small World), which is available in pgvector. This would reduce search latency from linear O(N) to logarithmic O(log N), enabling real-time search over millions of documents.

3. Streaming API Responses
Problem: The user has to wait for the entire answer to be generated before seeing any text, which can feel slow.

Solution: I would refactor the /api/query endpoint to use Server-Sent Events (SSE). This would allow the backend to stream the generated answer token-by-token to the frontend, dramatically improving the perceived responsiveness of the application.

4. Enhanced Observability
Problem: The current application has minimal logging and no metrics.

Solution: I would integrate structured logging (e.g., using structlog) and expose key application metrics (e.g., query latency, tokens generated) in a Prometheus format. This data is crucial for monitoring system health, performance, and cost in a production environment.

5. Infrastructure as Code (IaC)
Problem: The Vercel project and its settings are configured manually.

Solution: While we have a CI/CD pipeline, I would add Terraform to manage the Vercel project itself, including environment variables and domain settings. This ensures the entire cloud infrastructure is version-controlled and reproducible.