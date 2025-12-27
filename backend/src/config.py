import os

# Model Configuration
LLM_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"

# Paths
VECTOR_STORE_PATH = "vector_store_index"
UPLOAD_DIR = "uploads"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
