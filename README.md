# 🧠 Shopos RAG System

This repository contains a complete, **production-ready Retrieval-Augmented Generation (RAG) system**. It features:

- A custom vector database with `pgvector` support
- A full-stack web app with real-time streaming chat
- Automated CI/CD pipeline to AWS EC2 with Terraform + GitHub Actions

---

## ✨ Features

- ✅ **Custom Vector DB**: Built from scratch in Python, with optional `pgvector` for persistence
- ⚡ **High-Speed ANN Search**: Uses HNSW index for fast vector retrieval
- 🧠 **Advanced RAG Pipeline**: Bi-encoder → cross-encoder re-ranking → RRF fusion
- 💬 **Streaming Chat Interface**: Real-time token-by-token response via Server-Sent Events (SSE)
- 🔧 **FastAPI Backend**: Serves both REST API and frontend UI
- 🚀 **CI/CD + Infra as Code**: Fully automated AWS deployment with Terraform + GitHub Actions
- 📊 **Built-in Observability**: Prometheus `/metrics` + structured logging

---

## 🛠️ Tech Stack

| Category     | Technologies                                                                 |
|--------------|-------------------------------------------------------------------------------|
| **Backend**  | FastAPI, Gunicorn                                                            |
| **Database** | PostgreSQL + `pgvector`                                                      |
| **Frontend** | HTML, Tailwind CSS, Vanilla JS (with SSE)                                    |
| **AI Models**| `bge-micro` (embedding), `MiniLM` (re-ranking), `distilgpt2` (generation)     |
| **DevOps**   | Docker, Docker Compose, Terraform, GitHub Actions                            |
| **Cloud**    | AWS EC2                                                                      |

---

## 🚀 Getting Started (Local)

> This project is fully containerized — ready to spin up locally in minutes.

### 🧩 Prerequisites

- Docker + Docker Compose
- Python 3.10+
- PostgreSQL client (optional for manual DB access)

### 📦 Clone the Repository

```bash
git clone (https://github.com/akhilsingh-git/Shopos-RagApp.git)

🛠️ Create a .env File
DATABASE_URL=postgresql://raguser:ragpassword@localhost:5432/ragdb

🐘 Start the Vector Database
docker-compose up -d db

🧱 Run Migrations + Load Data
pip install -r requirements.txt
python migrate_db.py

🚀 Launch the Full App

docker-compose up --build
Visit: http://localhost:8000

📈 Roadmap / Future Improvements
Area	Enhancement
Evaluation	Add RAG evaluation pipeline using RAGAs
Model Quality	Upgrade to LLaMA 3 or Mistral 7B with quantization
Database Resilience	Move from containerized Postgres to managed RDS
Frontend Hosting	Serve static UI via Vercel or AWS S3 + CloudFront
Security	Add AuthN/Z to APIs + stricter AWS security group rules

🖼️ Screenshot
![Diagram](https://github.com/user-attachments/assets/62762616-a7f5-4e5b-9e6a-c4bb243d8c66)

🙋‍♂️ Questions?
Feel free to open issues or reach out at singhakhil2018@gmail.com
