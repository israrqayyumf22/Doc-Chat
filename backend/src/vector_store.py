from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from typing import List, Optional
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

def add_documents_to_store(vector_store: FAISS, chunks: List[Document], embedding_model):
    """
    Adds new documents to an existing FAISS vector store.
    
    Args:
        vector_store: Existing FAISS vector store
        chunks: New document chunks to add
        embedding_model: Embedding model for the new chunks
    
    Returns:
        Updated vector store
    """
    if vector_store is None:
        # If no existing store, create a new one
        return create_vector_store(chunks, embedding_model)
    
    # Add documents to existing store
    vector_store.add_documents(chunks)
    return vector_store

def delete_document_from_store(vector_store: FAISS, filename: str, uploaded_at: str, embedding_model) -> Optional[FAISS]:
    """
    Deletes a document from the vector store by filtering out chunks with matching source and uploaded_at.
    
    Args:
        vector_store: Existing FAISS vector store
        filename: Source filename to delete
        uploaded_at: Upload timestamp to uniquely identify the document
        embedding_model: Embedding model to rebuild the store
    
    Returns:
        New vector store without the deleted document, or None if no documents remain
    """
    if vector_store is None:
        return None
    
    # Get all documents from the vector store
    all_docs = []
    docstore = vector_store.docstore
    index_to_docstore_id = vector_store.index_to_docstore_id
    
    # Extract all documents
    for idx in range(len(index_to_docstore_id)):
        doc_id = index_to_docstore_id[idx]
        doc = docstore.search(doc_id)
        if doc:
            all_docs.append(doc)
    
    # Filter out documents with matching source and uploaded_at
    filtered_docs = [
        doc for doc in all_docs
        if not (doc.metadata.get('source') == filename and doc.metadata.get('uploaded_at') == uploaded_at)
    ]
    
    print(f"Deleting '{filename}': {len(all_docs)} chunks before, {len(filtered_docs)} chunks after, {len(all_docs) - len(filtered_docs)} removed")
    
    # If no documents remain, return None
    if not filtered_docs:
        print("No documents remain after deletion.")
        return None
    
    # Rebuild vector store with remaining documents
    new_vector_store = FAISS.from_documents(
        documents=filtered_docs,
        embedding=embedding_model,
        distance_strategy=DistanceStrategy.COSINE
    )
    
    return new_vector_store

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
