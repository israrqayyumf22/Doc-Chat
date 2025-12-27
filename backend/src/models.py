from langchain_ollama import OllamaEmbeddings, ChatOllama
from .config import EMBEDDING_MODEL, LLM_MODEL

def get_embeddings_model():
    """
    Returns the Ollama Embeddings model.
    """
    return OllamaEmbeddings(model=EMBEDDING_MODEL)

def get_llm_model():
    """
    Returns the ChatOllama model.
    """
    return ChatOllama(model=LLM_MODEL)
