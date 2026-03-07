import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Prioritize Streamlit Secrets for Cloud deployment, fallback to environment/local
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    try:
        DATABASE_URL = st.secrets.get("DATABASE_URL")
    except:
        pass

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mudric_portfolio"

# Create engine with some defaults for performance
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Context manager style for non-FastAPI/Streamlit use cases"""
    return SessionLocal()
