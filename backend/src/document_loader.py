from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document
import os
from datetime import datetime

def load_and_split_pdf(file_path: str, uploaded_at: str = None) -> List[Document]:
    """
    Loads a PDF file and splits it into chunks.
    Adds metadata with source filename and upload timestamp for tracking.
    
    Args:
        file_path: Path to the PDF file
        uploaded_at: ISO format timestamp of when file was uploaded
    """
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    
    chunks = text_splitter.split_documents(docs)
    
    # Add source filename and upload timestamp to metadata for each chunk
    filename = os.path.basename(file_path)
    if uploaded_at is None:
        uploaded_at = datetime.now().isoformat()
    
    for chunk in chunks:
        chunk.metadata['source'] = filename
        chunk.metadata['uploaded_at'] = uploaded_at
    
    return chunks
