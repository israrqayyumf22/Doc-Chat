from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from typing import List
import os
from .config import get_vector_store_path, MODEL_PROVIDER

def create_vector_store(chunks: List[Document], embedding_model):
    """
    Creates a FAISS vector store from document chunks.
    """
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model,
        distance_strategy=DistanceStrategy.COSINE
    )
    return vector_store

def save_vector_store(vector_store, provider=None):
    """
    Saves the vector store to disk using provider-specific path.
    
    Args:
        vector_store: The FAISS vector store to save
        provider: "ollama" or "openai". If None, uses MODEL_PROVIDER from config.
    """
    if provider is None:
        provider = MODEL_PROVIDER
    
    store_path = get_vector_store_path(provider)
    
    if os.path.exists(store_path):
        import shutil
        shutil.rmtree(store_path)
    
    vector_store.save_local(store_path)
    print(f"Vector store saved to: {store_path}")

def load_vector_store(embedding_model, provider=None):
    """
    Loads the vector store from disk if it exists, using provider-specific path.
    
    Args:
        embedding_model: The embedding model to use for loading
        provider: "ollama" or "openai". If None, uses MODEL_PROVIDER from config.
    
    Returns:
        FAISS vector store if found, None otherwise
    """
    if provider is None:
        provider = MODEL_PROVIDER
    
    store_path = get_vector_store_path(provider)
    
    if os.path.exists(store_path):
        print(f"Loading vector store from: {store_path}")
        return FAISS.load_local(
            store_path, 
            embedding_model, 
            allow_dangerous_deserialization=True
        )
    
    print(f"No vector store found at: {store_path}")
    return None
