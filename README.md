# 🧠 ShopOS-Production-Ready RAG System

A fully modernized Retrieval-Augmented Generation (RAG) system featuring:

- **Persistent vector database** with PostgreSQL + pgvector
- **Scalable ANN search** using HNSW
- **Advanced RAG pipeline** (bi-encoder → cross-encoder re-ranking → RRF fusion, upgraded to TinyLlama)
- **Streaming chat interface** built with SSE for real-time responses
- **FastAPI + Gunicorn backend** containerized and orchestrated with Docker
- **CI/CD pipeline** with Terraform & GitHub Actions for automated provisioning & deployment to AWS EC2
- **Nginx reverse proxy** for clean domain access
- **Managed secrets** injected via environment variables and GitHub Secrets

> 🎯 This project evolved from a simple NumPy prototype into a robust, production-grade application.

---

## 📝 Project Evolution

| Phase                 | Improvement                                                                                     |
|----------------------|--------------------------------------------------------------------------------------------------|
| **In-memory DB → Persistent** | Swapped NumPy array for PostgreSQL + pgvector to support durable and scalable storage.         |
| **Exact → Approximate Search**  | Added HNSW index to scale ANN search from O(N) to O(log N) latency.                             |
| **Basic → Advanced Retrieval** | Implemented two-stage retrieval: fast bi-encoder search → cross-encoder re-ranking → RRF fusion; upgraded generator from GPT-2 to TinyLlama. |
| **Sync → Streaming UI**         | Redesigned UI to use Server-Sent Events (SSE) for token-by-token response streaming.             |
| **Manual → Automated Deploy**   | Introduced Terraform + GitHub Actions to provision EC2, deploy containers, migrate DB, update DNS. |
| **Direct Access → Reverse Proxy** | Added Nginx to serve the app on port 80 via clean domain (`your-domain.duckdns.org`).            |
| **Hardcoded → Secure Secrets**  | Migrated secrets to environment variables managed via GitHub Secrets; removed from source code.     |

---

## 📁 Repository Structure

```text
.github/workflows/      # CI/CD definition (deploy.yml)
api/                    # FastAPI app core logic & routes
nginx/                  # nginx.conf for reverse proxy
public/                 # Frontend files (index.html, script.js)
.env                    # Local env variables (not committed)
docker-compose.yml      # Defines app, db, nginx services
Dockerfile              # Builds the FastAPI application
main.tf                 # Terraform infra provisioning (EC2, SG, etc.)
migrate_db.py           # Initialize PostgreSQL + load documents.json
requirements.txt        # Python dependencies
🚀 Running Locally
Prerequisites
Docker & Docker Compose installed

Python 3.10+ (for migration script)

Quick Setup

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Create .env with:

DATABASE_URL=postgresql://username:password@localhost:5432/ragdb

# Spin up the database
docker-compose up -d db

# Migrate and load data
pip install -r requirements.txt
python migrate_db.py

# Launch the full stack
docker-compose up --build
Visit: http://localhost

###✅ Automated Deployment to AWS EC2
Prerequisites
AWS account & permissions to manage EC2, SGs, etc.

DuckDNS account with an existing domain

AWS EC2 SSH key pair with PEM file

Setup
Set your AWS key name in main.tf:
key_name = "YourEC2KeyName"
In GitHub Settings → Secrets and variables → Actions, add:

AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
EC2_SSH_PRIVATE_KEY   # PEM contents
DUCKDNS_DOMAIN
DUCKDNS_TOKEN
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB

Deploy
Push any changes to the main-V2 branch. The GitHub Actions workflow will:

Run terraform apply to provision AWS resources

SSH into the EC2 instance and deploy containers

Run migrations and seed the database

Update your DuckDNS domain with the new public IP

Provide a final URL for your live app 

http://shopos-rag.duckdns.org/

####📈 Extension Ideas
Add offline RAG evaluation (e.g., RAGAs) for quality tracking

Upgrade to a more capable generator (fine-tuned LLaMA)

Migrate database to managed AWS RDS for high availability

Deploy frontend separately (e.g., Vercel or S3 + CloudFront)

Add authentication and tighten security rules on EC2

#####🖼 Screenshot
<!-- TODO: Add a screenshot or demo GIF here -->
🧭 License & Contributions
Licensed under MIT. Contributions, feedback, and issue reports are welcome!

#######💬 Need Help?
Open an issue or contact me via GitHub.

Enjoy exploring the RAG system!

The writeup is present in submission.doc
