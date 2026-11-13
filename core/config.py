"""Central configuration for HGrid247 AI Assistant."""

import os

from dotenv import load_dotenv


load_dotenv()

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "hgrid247_docs")

# Embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# LLM
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# RAG
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "10"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "8"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
