import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model Provider Configuration
# Options: "ollama" or "openai"
MODEL_PROVIDER = "openai"  # possible values: "ollama", "openai"

# Ollama Model Configuration
OLLAMA_LLM_MODEL = "llama3.2:1b"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"

# OpenAI Model Configuration
OPENAI_LLM_MODEL = "gpt-3.5-turbo"  # or "gpt-4", "gpt-4-turbo", etc.
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large", "text-embedding-ada-002"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Set via environment variable

# Legacy variables for backwards compatibility
LLM_MODEL = OLLAMA_LLM_MODEL
EMBEDDING_MODEL = OLLAMA_EMBEDDING_MODEL

# Paths
VECTOR_STORE_PATH_OLLAMA = "vector_store_index_ollama"
VECTOR_STORE_PATH_OPENAI = "vector_store_index_openai"
UPLOAD_DIR = "uploads"

# Legacy path variable (for backwards compatibility)
VECTOR_STORE_PATH = VECTOR_STORE_PATH_OLLAMA

def get_vector_store_path(provider=None):
    """Get the appropriate vector store path based on provider."""
    if provider is None:
        provider = MODEL_PROVIDER
    
    if provider.lower() == "openai":
        return VECTOR_STORE_PATH_OPENAI
    elif provider.lower() == "ollama":
        return VECTOR_STORE_PATH_OLLAMA
    else:
        return VECTOR_STORE_PATH_OLLAMA  # Default to Ollama

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
