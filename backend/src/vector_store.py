from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from typing import List
import os
from .config import VECTOR_STORE_PATH

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

def save_vector_store(vector_store):
    """
    Saves the vector store to disk.
    """
    if os.path.exists(VECTOR_STORE_PATH):
        import shutil
        shutil.rmtree(VECTOR_STORE_PATH)
    vector_store.save_local(VECTOR_STORE_PATH)

def load_vector_store(embedding_model):
    """
    Loads the vector store from disk if it exists.
    """
    if os.path.exists(VECTOR_STORE_PATH):
        return FAISS.load_local(
            VECTOR_STORE_PATH, 
            embedding_model, 
            allow_dangerous_deserialization=True
        )
    return None
