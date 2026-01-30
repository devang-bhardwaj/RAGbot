"""
Configuration settings for RAGbot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq Configuration
def get_config(key, default=None):
    """Get config from Streamlit secrets or environment variables"""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

GROQ_API_KEY = get_config("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Supabase Configuration
SUPABASE_URL = get_config("SUPABASE_URL")
SUPABASE_KEY = get_config("SUPABASE_KEY")

# Pinecone Configuration
PINECONE_API_KEY = get_config("PINECONE_API_KEY")
PINECONE_INDEX_NAME = get_config("PINECONE_INDEX_NAME")

# ChromaDB Configuration (Legacy/Fallback)
CHROMA_PERSIST_DIR = "./chroma_db"

# Embedding Model (Free, runs locally)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Document Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Supported file types
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]
