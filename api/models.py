from sqlalchemy import Column, String, Text
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    text_content = Column(Text, nullable=False)
    embedding = Column(Vector(384))
