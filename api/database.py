import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load the DATABASE_URL from Netlify's environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if the database URL is available
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get a DB session in API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
