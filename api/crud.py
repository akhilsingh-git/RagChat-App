from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
import numpy as np
from . import models

def create_document(db: Session, doc_id: str, text: str, embedding: np.ndarray):
    db_document = models.Document(id=doc_id, text_content=text, embedding=embedding)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_top_k_documents(db: Session, query_embedding: np.ndarray, k: int):
    # pgvector's <#> operator calculates the dot product
    # and sorts by it in descending order (highest dot product first)
    results = db.query(models.Document).order_by(models.Document.embedding.max_inner_product(query_embedding)).limit(k).all()
    return results