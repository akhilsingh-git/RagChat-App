import json
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import text
# Import DATABASE_URL to check it
from api.database import SessionLocal, engine, DATABASE_URL
from api import models, crud

def migrate_data():
    # Add a check to ensure the environment variable is loaded
    if not DATABASE_URL:
        print("🔴 Error: DATABASE_URL environment variable not found.")
        print("Please ensure you have a .env file in the project root with the DATABASE_URL set.")
        return

    db: Session = SessionLocal()
    try:
        # Enable the pgvector extension
        print("Enabling pgvector extension...")
        db.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
        db.commit()
        print("pgvector extension enabled.")

        # Create tables
        print("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("Tables created.")

        # --- NEW: Create HNSW index for ANN search ---
        print("Creating HNSW index for high-speed ANN search...")
        # We use vector_ip_ops for dot product (maximum inner product) search.
        # This index dramatically speeds up similarity search on large datasets.
        db.execute(text('CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx ON documents USING hnsw (embedding vector_ip_ops);'))
        db.commit()
        print("HNSW index created.")

        # Initialize models
        embedding_model = SentenceTransformer('TaylorAI/bge-micro')

        # Load data from JSON file
        print("Loading data from documents.json...")
        with open('documents.json', 'r') as f:
            documents = json.load(f)
        print(f"Found {len(documents)} documents.")

        # Generate embeddings and insert into DB
        # Check if data already exists to avoid duplication
        doc_count = db.query(models.Document).count()
        if doc_count > 0:
            print(f"Database already contains {doc_count} documents. Skipping data insertion.")
        else:
            for doc in documents:
                print(f"Processing document {doc['id']}...")
                embedding = embedding_model.encode(doc['data'])
                crud.create_document(db, doc_id=doc['id'], text=doc['data'], embedding=embedding)
            print("Data insertion complete.")
        
        print("✅ Data migration complete.")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()