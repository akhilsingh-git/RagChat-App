from sqlalchemy import Column, String, Text
from pgvector.sqlalchemy import Vector
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    text_content = Column(Text, nullable=False)
    embedding = Column(Vector(384)) # 384 is the dimension of bge-micro