from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from datetime import datetime
from src.config import get_upload_dir, get_vector_store_path
from src.document_loader import load_and_split_pdf
from src.models import get_embeddings_model, get_llm_model
from src.vector_store import create_vector_store, save_vector_store, load_vector_store
from src.rag import create_rag_chain
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to hold models and vector store
models = {}
vector_store = None

@app.on_event("startup")
async def startup_event():
    global models, vector_store
    import src.rag
    from src.config import MODEL_PROVIDER
    
    print(f"DEBUG: src.rag file: {src.rag.__file__}")
    print(f"Using MODEL_PROVIDER: {MODEL_PROVIDER}")
    
    # Initialize models with the configured provider
    models["embedding"] = get_embeddings_model(provider=MODEL_PROVIDER)
    models["llm"] = get_llm_model(provider=MODEL_PROVIDER)
    
    # Try loading existing vector store for the current provider
    loaded_vs = load_vector_store(models["embedding"], provider=MODEL_PROVIDER)
    if loaded_vs:
        vector_store = loaded_vs
        print("Vector store loaded successfully.")
    else:
        print("No existing vector store found.")

class QueryRequest(BaseModel):
    query: str

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    global vector_store
    from src.config import MODEL_PROVIDER
    from src.vector_store import add_documents_to_store
    
    try:
        # Get provider-specific upload directory
        upload_dir = get_upload_dir(provider=MODEL_PROVIDER)
        file_path = os.path.join(upload_dir, file.filename)
        
        # Save file first
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file modification timestamp AFTER saving (Clock B)
        stat = os.stat(file_path)
        uploaded_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        print(f"Ingesting file: {file.filename} (provider: {MODEL_PROVIDER})")
        print(f"Using file timestamp: {uploaded_at}")
        chunks = load_and_split_pdf(file_path, uploaded_at=uploaded_at)
        
        if not chunks:
             raise HTTPException(status_code=400, detail="No text found in PDF.")

        print(f"Created {len(chunks)} chunks from PDF.")
        
        # Add to existing vector store instead of replacing
        vector_store = add_documents_to_store(vector_store, chunks, models["embedding"])
        save_vector_store(vector_store, provider=MODEL_PROVIDER)
        print("Documents added to vector store and saved successfully.")
        
        return {
            "message": "Document ingested and added to vector store successfully.",
            "chunks": len(chunks),
            "uploaded_at": uploaded_at
        }
    except Exception as e:
        print(f"Error executing ingest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: QueryRequest):
    global vector_store
    from src.config import MODEL_PROVIDER
    
    if not vector_store:
        raise HTTPException(status_code=400, detail="No documents ingested yet.")
    
    try:
        # Always get a fresh LLM instance to avoid global state issues
        llm = get_llm_model(provider=MODEL_PROVIDER)
        print(f"DEBUG: Instantiated LLM: {type(llm)}")
        
        chain = create_rag_chain(vector_store, llm)
        response = chain.invoke({"input": request.query})
        
        # Handle simple string response (fallback if full dict chain fails)
        if isinstance(response, str):
            return {"answer": response, "context": []}
            
        return {"answer": response["answer"], "context": [doc.page_content for doc in response["context"]]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoints for document management

@app.get("/documents")
async def get_documents():
    """
    Get list of all uploaded documents with metadata.
    Returns document names, extensions, size, and upload date.
    """
    from src.config import MODEL_PROVIDER
    
    try:
        upload_dir = get_upload_dir(provider=MODEL_PROVIDER)
        
        if not os.path.exists(upload_dir):
            return {"documents": [], "provider": MODEL_PROVIDER}
        
        documents = []
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Get file stats (Clock B - filesystem time)
            stat = os.stat(file_path)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Get file extension
            name, extension = os.path.splitext(filename)
            
            documents.append({
                "filename": filename,
                "name": name,
                "extension": extension.lstrip('.'),
                "size": file_size,
                "sizeFormatted": format_file_size(file_size),
                "uploadedOn": modified_time.isoformat(),
                "uploadedOnFormatted": modified_time.strftime("%b %d, %Y %I:%M %p")
            })
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x['uploadedOn'], reverse=True)
        
        return {
            "documents": documents,
            "provider": MODEL_PROVIDER,
            "count": len(documents)
        }
    except Exception as e:
        print(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{filename}")
async def get_document(filename: str):
    """
    Download/view a specific document by filename.
    """
    from src.config import MODEL_PROVIDER
    
    try:
        upload_dir = get_upload_dir(provider=MODEL_PROVIDER)
        file_path = os.path.join(upload_dir, filename)
        
        # Security check: ensure file is within upload directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Document not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(filename: str, uploaded_at: str):
    """
    Delete a document and its embeddings from the vector store.
    Requires both filename and uploaded_at timestamp to uniquely identify the document.
    
    Query parameters:
        uploaded_at: ISO format timestamp of when the file was uploaded
    """
    global vector_store
    from src.config import MODEL_PROVIDER
    from src.vector_store import delete_document_from_store
    
    try:
        upload_dir = get_upload_dir(provider=MODEL_PROVIDER)
        file_path = os.path.join(upload_dir, filename)
        
        # Security check: ensure file is within upload directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete from vector store first
        if vector_store:
            vector_store = delete_document_from_store(
                vector_store,
                filename,
                uploaded_at,
                models["embedding"]
            )
            
            # Save updated vector store (or delete if empty)
            if vector_store:
                save_vector_store(vector_store, provider=MODEL_PROVIDER)
                print(f"Vector store updated after deleting {filename}")
            else:
                # If no documents remain, delete the vector store directory
                store_path = get_vector_store_path(provider=MODEL_PROVIDER)
                if os.path.exists(store_path):
                    shutil.rmtree(store_path)
                    print("Vector store deleted (no documents remaining)")
        
        # Delete the physical file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {filename}")
        else:
            raise HTTPException(status_code=404, detail="Document file not found")
        
        return {
            "message": f"Document '{filename}' and its embeddings deleted successfully.",
            "filename": filename
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
