# Backend - RAG-based PDF Question Answering System

## 📋 Overview

This is a FastAPI-based backend service that implements a Retrieval-Augmented Generation (RAG) system for question answering over PDF documents. The system allows users to upload PDF documents, which are then processed and indexed for efficient semantic search and question answering.

**Flexible Model Support**: The backend supports both **local models via Ollama** (100% free, privacy-first) and **OpenAI models** (cloud-based, requires API key). You can easily switch between providers based on your needs.

## 🏗️ Architecture

The backend uses the following components:

1. **FastAPI** - Modern web framework for building APIs
2. **LangChain** - Framework for building LLM applications
3. **Ollama** OR **OpenAI** - LLM and embedding model providers (switchable)
4. **FAISS** - Vector database for efficient similarity search
5. **PyMuPDF** - PDF processing library

### RAG Pipeline Flow:

```
PDF Upload → Text Extraction → Chunking → Metadata Tagging → Embeddings → FAISS Vector Store
                                              ↓                                    ↓
                                    (source + uploaded_at)              (Add to existing store)
                                                                                   ↓
User Query → Embedding → Similarity Search (ALL docs) → Context Retrieval → LLM → Answer

Document Deletion → Filter by (source + uploaded_at) → Rebuild Vector Store → Updated Index
```

**Key Features:**
- ✅ **Multi-Document Support**: Upload unlimited PDFs, query across all simultaneously
- ✅ **Incremental Addition**: New documents are added to existing vector store (not replaced)
- ✅ **Unique Tracking**: Each document tagged with `source` (filename) + `uploaded_at` (timestamp)
- ✅ **Selective Deletion**: Delete specific documents without affecting others
- ✅ **Provider Separation**: Separate vector stores for Ollama and OpenAI

## 🤖 Models Used

The system supports two model providers that you can switch between in [`src/config.py`](src/config.py):

### Option 1: Ollama (Local, Free) - Default

#### LLM (Language Model)
- **Model**: `llama3.2:1b` (Llama 3.2 - 1 billion parameters)
- **Provider**: Ollama (local)
- **Purpose**: Generates answers based on retrieved context
- **Cost**: 100% FREE (runs locally)
- **Requirements**: ~2GB disk space, 4GB RAM minimum

#### Embedding Model
- **Model**: `nomic-embed-text`
- **Provider**: Ollama (local)
- **Purpose**: Converts text into vector embeddings for semantic search
- **Cost**: 100% FREE (runs locally)
- **Requirements**: ~274MB disk space

> **Note**: Ollama models run completely locally. No API keys required, no usage limits, and your data never leaves your machine!

### Option 2: OpenAI (Cloud-based)

#### LLM (Language Model)
- **Model**: `gpt-3.5-turbo` (configurable to `gpt-4`, `gpt-4-turbo`, etc.)
- **Provider**: OpenAI API
- **Purpose**: Generates answers based on retrieved context
- **Cost**: Pay-per-use (see [OpenAI Pricing](https://openai.com/api/pricing/))
- **Requirements**: OpenAI API key, internet connection

#### Embedding Model
- **Model**: `text-embedding-3-small` (configurable to `text-embedding-3-large`, etc.)
- **Provider**: OpenAI API
- **Purpose**: Converts text into vector embeddings for semantic search
- **Cost**: Pay-per-use (very affordable)
- **Requirements**: OpenAI API key, internet connection

> **Note**: OpenAI provides higher quality responses but requires an API key and internet connection. Best for production use or when local resources are limited.

## 🔌 API Endpoints

### 1. **POST /ingest**
Uploads and processes a PDF document, adding it to the vector store.

**Request:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "message": "Document ingested and added to vector store successfully.",
  "chunks": 42,
  "uploaded_at": "2025-12-28T10:30:45.123456"
}
```

**What it does:**
- Accepts PDF file upload
- Extracts text from PDF
- Splits text into manageable chunks (~1000 chars each with 200 char overlap)
- Adds metadata to each chunk: `source` (filename) and `uploaded_at` (timestamp)
- Creates embeddings for each chunk
- **Adds** chunks to existing vector store (doesn't replace existing documents!)
- Saves updated vector store to disk
- Returns upload timestamp for future document identification

**✨ Multi-Document Support:**
- Upload multiple PDFs and query across all of them!
- Each document is tracked with unique `source` + `uploaded_at` combination
- You can upload files with the same name multiple times (each upload gets a unique timestamp)
- All documents remain searchable until explicitly deleted

---

### 2. **POST /chat**
Asks a question about the ingested documents (searches across ALL uploaded documents).

**Request:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of the document?"}'
```

**Request Body:**
```json
{
  "query": "Your question here"
}
```

**Response:**
```json
{
  "answer": "The answer generated by the LLM based on the document context.",
  "context": [
    "Relevant chunk 1 from the document...",
    "Relevant chunk 2 from the document...",
    "Relevant chunk 3 from the document..."
  ]
}
```

**What it does:**
- Takes user's question
- Converts question to embedding
- Searches for top 3 most relevant chunks from **all documents** in the vector store
- Sends question + context to LLM
- Returns generated answer with source context

---

### 3. **GET /documents**
Retrieves a list of all uploaded documents with metadata.

**Request:**
```bash
curl -X GET "http://localhost:8000/documents"
```

**Response:**
```json
{
  "documents": [
    {
      "filename": "research_paper.pdf",
      "name": "research_paper",
      "extension": "pdf",
      "size": 2457600,
      "sizeFormatted": "2.3 MB",
      "uploadedOn": "2025-12-28T10:30:45.123456",
      "uploadedOnFormatted": "Dec 28, 2025 10:30 AM"
    },
    {
      "filename": "report.pdf",
      "name": "report",
      "extension": "pdf",
      "size": 1048576,
      "sizeFormatted": "1.0 MB",
      "uploadedOn": "2025-12-28T09:15:30.654321",
      "uploadedOnFormatted": "Dec 28, 2025 09:15 AM"
    }
  ],
  "provider": "openai",
  "count": 2
}
```

**What it does:**
- Lists all documents uploaded for the current provider
- Returns file metadata (name, size, upload timestamp)
- Sorted by upload date (newest first)

---

### 4. **GET /documents/{filename}**
Downloads or views a specific document.

**Request:**
```bash
curl -X GET "http://localhost:8000/documents/research_paper.pdf"
```

**Response:**
- Returns the PDF file for download/viewing

**What it does:**
- Retrieves the physical PDF file
- Includes security check to prevent directory traversal attacks
- Returns 404 if document not found

---

### 5. **DELETE /documents/{filename}**
Deletes a document and its embeddings from the vector store.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/documents/research_paper.pdf?uploaded_at=2025-12-28T10:30:45.123456"
```

**Query Parameters:**
- `uploaded_at` (required): ISO format timestamp from when the file was uploaded

**Response:**
```json
{
  "message": "Document 'research_paper.pdf' and its embeddings deleted successfully.",
  "filename": "research_paper.pdf"
}
```

**What it does:**
- Deletes the physical PDF file from uploads directory
- Removes all embeddings/chunks associated with that specific document
- Uses **both** `filename` AND `uploaded_at` to uniquely identify the document
- Rebuilds vector store without the deleted document's chunks
- If no documents remain, deletes the entire vector store

**🔒 Deletion Strategy - Unique Document Identification:**

The system uses a **compound key** (`source` + `uploaded_at`) to uniquely identify documents:

1. **Why this matters:** You can upload files with the same name multiple times
   - Upload `report.pdf` at 10:00 AM → `{source: "report.pdf", uploaded_at: "2025-12-28T10:00:00"}`
   - Upload `report.pdf` again at 11:00 AM → `{source: "report.pdf", uploaded_at: "2025-12-28T11:00:00"}`
   - Both versions coexist in the vector store!

2. **How deletion works:**
   - Loads the existing vector store
   - Extracts all document chunks with their metadata
   - Filters out chunks where **BOTH** `metadata['source'] == filename` **AND** `metadata['uploaded_at'] == timestamp`
   - Rebuilds vector store with remaining chunks (no re-embedding needed - vectors already computed!)
   - Deletes the physical file

3. **Why rebuild instead of direct deletion:**
   - FAISS doesn't support deleting individual vectors by ID
   - We filter chunks and create a new index structure from existing embeddings
   - Fast operation since embeddings are already computed
   - Ensures clean index without fragmentation

**Example Scenario:**
```bash
# Upload same file twice
POST /ingest (report.pdf at 10:00) → uploaded_at: "2025-12-28T10:00:00"
POST /ingest (report.pdf at 11:00) → uploaded_at: "2025-12-28T11:00:00"

# Delete only the first version
DELETE /documents/report.pdf?uploaded_at=2025-12-28T10:00:00
✅ First version deleted, second version still searchable!

# Query still works with the remaining version
POST /chat → Returns answers from the 11:00 version
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **Choose your model provider**:
   - **Ollama** (recommended for local/free setup) - Install Ollama
   - **OpenAI** (for cloud-based, higher quality) - Get an API key from [OpenAI](https://platform.openai.com/api-keys)

---

### Setup Option 1: Using Ollama (Local, Free)

#### Step 1: Install Ollama

**Windows:**
- Download from [ollama.com](https://ollama.com)
- Run the installer
- Ollama will start automatically

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Step 2: Pull Required Models

Open a terminal and run:

```bash
# Pull the LLM model (Llama 3.2 - 1B)
ollama pull llama3.2:1b

# Pull the embedding model (Nomic Embed Text)
ollama pull nomic-embed-text
```

**Model Download Sizes:**
- `llama3.2:1b` - ~1.3 GB
- `nomic-embed-text` - ~274 MB

#### Step 3: Set Up Python Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Configuration

The default configuration in [`src/config.py`](src/config.py) is already set to use Ollama:

```python
MODEL_PROVIDER = "ollama"  # Default
```

No additional configuration needed!

#### Step 5: Run the Backend

```bash
# Make sure Ollama is running (should be automatic)
# Then start the FastAPI server
python main.py
```

---

### Setup Option 2: Using OpenAI (Cloud-based)

#### Step 1: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (you won't see it again!)

#### Step 2: Set Up Python Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies (includes OpenAI packages)
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables

Create or edit the `.env` file in the backend directory:

```bash
# .env file
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

> **Important**: Never commit your `.env` file to version control. It's already in `.gitignore`.

#### Step 4: Update Configuration

Edit [`src/config.py`](src/config.py) to use OpenAI:

```python
MODEL_PROVIDER = "openai"  # Change from "ollama" to "openai"

# Optionally customize models:
OPENAI_LLM_MODEL = "gpt-3.5-turbo"  # or "gpt-4", "gpt-4-turbo"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
```

#### Step 5: Run the Backend

```bash
python main.py
```

---

### Both Options: Access the API

The server will start on `http://localhost:8000`

You can view the auto-generated API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📁 Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (API keys) - DO NOT COMMIT
├── .env.example                 # Example environment file (safe to commit)
├── .gitignore                   # Git ignore rules
├── uploads_ollama/              # Uploaded PDFs for Ollama provider
├── uploads_openai/              # Uploaded PDFs for OpenAI provider
├── vector_store_index_ollama/   # FAISS vector store for Ollama embeddings
│   └── index.faiss              # Ollama vector index file
├── vector_store_index_openai/   # FAISS vector store for OpenAI embeddings
│   └── index.faiss              # OpenAI vector index file
└── src/
    ├── __init__.py
    ├── config.py                # Configuration (model provider, paths)
    ├── models.py                # LLM and embedding model initialization
    ├── document_loader.py       # PDF loading, chunking, and metadata tagging
    ├── vector_store.py          # FAISS operations (create, add, delete, save, load)
    └── rag.py                   # RAG chain implementation
```

**Key Files:**
- **`document_loader.py`**: Extracts text from PDFs, splits into chunks, adds `source` + `uploaded_at` metadata
- **`vector_store.py`**: 
  - `create_vector_store()` - Creates new FAISS index
  - `add_documents_to_store()` - Adds documents to existing index (multi-document support!)
  - `delete_document_from_store()` - Filters and rebuilds index without specified document
  - `save_vector_store()` / `load_vector_store()` - Persistence
- **`main.py`**: API endpoints for ingest, chat, list documents, get document, delete document

---

## ⚙️ Configuration

### Switching Between Model Providers

In [`src/config.py`](src/config.py), you can easily switch between Ollama and OpenAI:

```python
# Model Provider Configuration
MODEL_PROVIDER = "ollama"  # Change to "openai" to use OpenAI models
```

**✨ Seamless Provider Switching**: The system maintains separate vector stores for each provider, so you can switch between Ollama and OpenAI without re-ingesting your documents. Once you've uploaded documents for each provider, switching is instant!

### Ollama Configuration

```python
# Ollama Model Configuration
OLLAMA_LLM_MODEL = "llama3.2:1b"           # Change to any Ollama model
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text" # Change to any Ollama embedding model
```

**Alternative Ollama Models:**

**LLM Models:**
- `llama3.2:1b` - Fast, lightweight (default)
- `llama3.2:3b` - Better quality, needs more RAM
- `llama3.2:latest` - Latest version
- `mistral:latest` - Alternative open-source LLM
- `phi:latest` - Microsoft's compact model

**Embedding Models:**
- `nomic-embed-text` - Best overall (recommended)
- `all-minilm` - Smaller, faster
- `mxbai-embed-large` - Higher quality

### OpenAI Configuration

```python
# OpenAI Model Configuration
OPENAI_LLM_MODEL = "gpt-3.5-turbo"  # or "gpt-4", "gpt-4-turbo", "gpt-4o"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
```

**OpenAI Model Options:**

**LLM Models:**
- `gpt-3.5-turbo` - Fast and affordable (default)
- `gpt-4` - Higher quality reasoning
- `gpt-4-turbo` - Faster GPT-4 with better pricing
- `gpt-4o` - Latest, most capable model

**Embedding Models:**
- `text-embedding-3-small` - Fast and affordable (default)
- `text-embedding-3-large` - Higher quality embeddings
- `text-embedding-ada-002` - Legacy model (still supported)

### Environment Variables (.env file)

```env
# OpenAI Configuration (only needed if using OpenAI)
OPENAI_API_KEY=sk-proj-your-api-key-here
```

### Path Configuration

```python
# Provider-Specific Vector Store Paths
VECTOR_STORE_PATH_OLLAMA = "vector_store_index_ollama"  # For Ollama embeddings
VECTOR_STORE_PATH_OPENAI = "vector_store_index_openai"  # For OpenAI embeddings

# Provider-Specific Upload Directories
UPLOAD_DIR_OLLAMA = "uploads_ollama"  # For Ollama PDF uploads
UPLOAD_DIR_OPENAI = "uploads_openai"  # For OpenAI PDF uploads

# Automatically selects the correct path based on MODEL_PROVIDER
def get_vector_store_path(provider=None):
    # Returns the appropriate vector store path for the current provider

def get_upload_dir(provider=None):
    # Returns the appropriate upload directory for the current provider
```

**Important**: The system now maintains **complete separation** for each provider:
- **Upload Directories**: PDFs uploaded with Ollama go to `uploads_ollama/`, PDFs uploaded with OpenAI go to `uploads_openai/`
- **Vector Stores**: Ollama embeddings stored in `vector_store_index_ollama/`, OpenAI embeddings stored in `vector_store_index_openai/`
- **Seamless Switching**: You can switch between providers without re-ingesting documents or managing file conflicts
- **Independent Persistence**: Each provider's uploads and vector stores persist independently

---

## 💡 How It Works

### Document Ingestion Process:

1. **PDF Upload**: User uploads a PDF via `/ingest` endpoint
2. **Text Extraction**: PyMuPDF extracts text from all pages
3. **Text Chunking**: Text is split into overlapping chunks (1000 chars with 200 char overlap)
4. **Metadata Tagging**: Each chunk receives metadata:
   - `source`: The filename (e.g., `"research_paper.pdf"`)
   - `uploaded_at`: ISO timestamp (e.g., `"2025-12-28T10:30:45.123456"`)
   - `page`: Original page number
   - `start_index`: Character position in document
5. **Embedding Generation**: Each chunk is converted to a vector using the embedding model
6. **Vector Storage**: Embeddings **added** to existing FAISS vector store (incremental, not replacement!)
7. **Persistence**: Updated vector store saved to disk for future use

**🔑 Unique Document Identification:**
- Each chunk contains `{"source": "filename.pdf", "uploaded_at": "2025-12-28T10:30:45.123456"}`
- This compound key allows multiple uploads of the same filename
- Example: Upload `report.pdf` twice → both versions coexist with different timestamps

### Question Answering Process:

1. **Query Embedding**: User's question is converted to a vector
2. **Similarity Search**: FAISS finds top 3 most similar chunks **across ALL uploaded documents**
3. **Context Building**: Retrieved chunks are formatted as context (may come from different documents!)
4. **Prompt Construction**: System prompt + context + user question combined
5. **LLM Generation**: LLM generates answer based on retrieved context
6. **Response**: Answer and source context returned to user

### Document Deletion Process:

1. **Identify Target**: Uses `filename` + `uploaded_at` to uniquely identify the document
2. **Load Vector Store**: Retrieves current FAISS index with all documents
3. **Extract Chunks**: Gets all document chunks with their metadata from the vector store
4. **Filter**: Removes chunks where `metadata['source'] == filename` AND `metadata['uploaded_at'] == timestamp`
5. **Rebuild Index**: Creates new FAISS index from remaining chunks (embeddings already computed, so fast!)
6. **Delete File**: Removes physical PDF from uploads directory
7. **Save**: Persists updated vector store (or deletes if no documents remain)

**Why Rebuild?**
- FAISS doesn't support direct deletion of vectors by ID
- We filter chunks and reconstruct the index structure
- Embeddings are already computed (no re-embedding needed!)
- Results in clean, unfragmented index
- Fast operation even with many documents

---

## 🆓 Cost & Privacy

### Ollama (Local) Option:

#### ✅ Completely Free:
- No API keys required
- No subscription fees
- No usage limits
- No hidden costs

#### 🔒 Privacy-First:
- All models run locally on your machine
- No data sent to external servers
- Documents stay on your computer
- Queries processed offline

#### 💻 System Requirements:
- **Minimum**: 4GB RAM, 5GB disk space
- **Recommended**: 8GB RAM, 10GB disk space
- **CPU**: Modern multi-core processor
- **GPU**: Optional (can accelerate inference)

### OpenAI (Cloud) Option:

#### 💳 Pay-Per-Use:
- Requires OpenAI API key
- Pay only for what you use
- Very affordable for moderate usage
- See [OpenAI Pricing](https://openai.com/api/pricing/) for details

**Typical Costs (as of 2025):**
- GPT-3.5-Turbo: ~$0.002 per 1K tokens
- GPT-4: ~$0.03 per 1K tokens
- Embeddings: ~$0.0001 per 1K tokens

Example: Processing a 50-page PDF and asking 100 questions might cost $0.50-$2.00 depending on the model.

#### 🌐 Requirements:
- Internet connection required
- Data sent to OpenAI servers (see [OpenAI Privacy Policy](https://openai.com/policies/privacy-policy))
- Higher quality responses
- Faster inference (no local compute needed)

---

## 🐛 Troubleshooting

### Ollama Issues

#### Ollama Not Found
```bash
# Check if Ollama is running
ollama list

# If not, start it manually
ollama serve
```

#### Models Not Available
```bash
# List installed models
ollama list

# Pull missing models
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

### OpenAI Issues

#### API Key Error
```
Error: OPENAI_API_KEY not set
```
**Solution**: Make sure you've created a `.env` file with your API key:
```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

#### Rate Limit Error
```
Error: Rate limit exceeded
```
**Solution**: OpenAI has rate limits. Wait a moment and try again, or upgrade your OpenAI plan.

#### Authentication Error
```
Error: Incorrect API key provided
```
**Solution**: Verify your API key is correct and active at [OpenAI Platform](https://platform.openai.com/api-keys).

### General Issues

#### Port Already in Use
```python
# In main.py, change the port:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed from 8000
```

#### Memory Issues (Ollama)
- Use a smaller model: `llama3.2:1b` instead of `llama3.2:3b`
- Reduce chunk retrieval: Edit `search_kwargs={"k": 2}` in `src/rag.py`
- Close other applications to free up RAM

#### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt

# For OpenAI specifically:
pip install openai langchain-openai
```

#### Switching Between Providers
**Good News**: The system now maintains **complete separation** between providers!

- When you switch `MODEL_PROVIDER` from "ollama" to "openai" (or vice versa), the system automatically uses the correct upload directory and vector store
- No need to delete or re-ingest documents when switching
- Each provider has its own dedicated directories:
  - **Ollama**: `uploads_ollama/` and `vector_store_index_ollama/`
  - **OpenAI**: `uploads_openai/` and `vector_store_index_openai/`

**First Time Setup**: If you haven't ingested documents for a provider yet, you'll need to upload them once via the `/ingest` endpoint. After that, both the uploaded PDFs and vector store persist, allowing you to switch freely.

**Example Workflow**:
1. Set `MODEL_PROVIDER = "ollama"` and upload a document → saved to `uploads_ollama/` with embeddings in `vector_store_index_ollama/`
2. Switch to `MODEL_PROVIDER = "openai"` and upload a document → saved to `uploads_openai/` with embeddings in `vector_store_index_openai/`
3. Now you can switch between providers anytime - each has its own complete ecosystem!

---

## 📚 Dependencies

See [`requirements.txt`](requirements.txt) for all dependencies:

**Core Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain>=0.3.0` - LLM framework
- `langchain-community>=0.3.0` - Community integrations
- `faiss-cpu` - Vector database
- `pymupdf` - PDF processing
- `python-multipart` - File upload support
- `numpy>=1.26.0` - Numerical computing
- `python-dotenv` - Environment variable management

**Provider-Specific:**
- `langchain-ollama` - Ollama integration (always installed)
- `openai` - OpenAI API client (optional, for OpenAI provider)
- `langchain-openai` - OpenAI LangChain integration (optional, for OpenAI provider)

> **Note**: OpenAI dependencies are included in `requirements.txt` but only used when `MODEL_PROVIDER = "openai"`. They won't affect Ollama usage.

---

## 🔗 Related Links

- [Ollama Documentation](https://ollama.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI Platform](https://platform.openai.com/api-keys) (Get API keys)
- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
