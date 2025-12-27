from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document

def load_and_split_pdf(file_path: str) -> List[Document]:
    """
    Loads a PDF file and splits it into chunks.
    """
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    
    chunks = text_splitter.split_documents(docs)
    return chunks
