Production-Ready RAG System
This repository contains a complete, production-ready Retrieval-Augmented Generation (RAG) system. It features a custom vector database, a full-stack web application with a real-time chat interface, and a fully automated CI/CD pipeline for deployment to AWS EC2.

<!-- Replace with a URL to a screenshot of your app -->

✨ Features
Custom Vector Database: Built from scratch using Python, supporting pgvector for persistent storage.

High-Speed Search: Implements an HNSW index for fast Approximate Nearest Neighbor (ANN) search.

Advanced RAG Pipeline: A sophisticated two-stage retrieval process using a bi-encoder for initial search and a cross-encoder for re-ranking, combined with Reciprocal Rank Fusion (RRF) for optimal relevance.

Streaming Chat Interface: A responsive frontend built with vanilla JavaScript that streams answers token-by-token for an excellent user experience.

Production-Grade Backend: A robust FastAPI backend serving the API and frontend.

End-to-End Automation: Fully automated infrastructure provisioning (Terraform) and application deployment (GitHub Actions) to AWS EC2.

Built-in Observability: Structured logging and a Prometheus metrics endpoint (/metrics) for monitoring.

🛠️ Technology Stack
Category

Technology

Backend

FastAPI, Gunicorn

Database

PostgreSQL + pgvector

Frontend

HTML, CSS, Vanilla JavaScript (with SSE)

AI Models

bge-micro (Embedding), ms-marco-MiniLM-L-6-v2 (Re-ranking), distilgpt2 (Generation)

DevOps

Docker, Docker Compose, Terraform, GitHub Actions

Cloud

AWS EC2

🚀 Running Locally
This project is fully containerized, making it easy to run locally with a single command.

Prerequisites:

Docker

Docker Compose

Instructions:

Clone the repository:

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

Create the environment file:
Create a .env file in the root directory and add the following line:

DATABASE_URL=postgresql://raguser:ragpassword@localhost:5432/ragdb

Start the database:

docker-compose up -d db

Run the database migration:
This script will create the necessary tables and populate the database with the sample data.

# Install dependencies locally for the script
pip install -r requirements.txt
python migrate_db.py

Launch the application:

docker-compose up --build

The application will be available at http://localhost:8000.

📈 Future Roadmap
While this is a complete and robust system, the following enhancements would be the next steps for scaling and improving quality:

RAG Evaluation Framework: Implement an offline evaluation pipeline using a framework like RAGAs to quantitatively measure faithfulness, answer_relevancy, and context_recall before deploying changes.

More Powerful Generator: Upgrade from distilgpt2 to a more advanced open-source model (like a fine-tuned Llama 3) for higher-quality answer synthesis.

Managed Database Service: For true production resilience, migrate the self-hosted PostgreSQL container to a managed service like Amazon RDS for PostgreSQL.

Separate Frontend Deployment: Decouple the frontend from the backend API by deploying it as a static site to a service like Vercel or AWS S3/CloudFront for better performance and scalability.

Enhanced Security: Implement authentication on API endpoints and tighten the security group rules to restrict access to known IP addresses.
