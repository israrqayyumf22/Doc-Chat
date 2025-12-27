from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from src.config import UPLOAD_DIR
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
    print(f"DEBUG: src.rag file: {src.rag.__file__}")
    models["embedding"] = get_embeddings_model()
    models["llm"] = get_llm_model()
    
    # Try loading existing vector store
    loaded_vs = load_vector_store(models["embedding"])
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
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"Ingesting file: {file.filename}")
        chunks = load_and_split_pdf(file_path)
        
        if not chunks:
             raise HTTPException(status_code=400, detail="No text found in PDF.")

        print(f"Created {len(chunks)} chunks from PDF.")
        vector_store = create_vector_store(chunks, models["embedding"])
        save_vector_store(vector_store)
        print("Vector store created and saved successfully.")
        
        return {"message": "Document ingested and vector store created successfully.", "chunks": len(chunks)}
    except Exception as e:
        print(f"Error executing ingest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: QueryRequest):
    global vector_store
    if not vector_store:
        raise HTTPException(status_code=400, detail="No documents ingested yet.")
    
    try:
        # Always get a fresh LLM instance to avoid global state issues
        llm = get_llm_model()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
