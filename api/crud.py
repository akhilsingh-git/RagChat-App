from sqlalchemy.orm import Session
import numpy as np
from . import models

def get_top_k_documents(db: Session, query_embedding: np.ndarray, k: int):
    """
    Performs a vector similarity search on the database.
    """
    # The <#> operator calculates the dot product for similarity
    results = db.query(models.Document).order_by(models.Document.embedding.max_inner_product(query_embedding)).limit(k).all()
    return results

