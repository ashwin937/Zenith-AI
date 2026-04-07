"""Main FastAPI application for Secure Local AI Chatbot."""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uvicorn

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="Zenith AI",
    description="Advanced local RAG-powered AI chatbot with secure, offline-first design",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import modules
from graph.workflow import run_graph
from graph.state import ChatState

# Lazy imports to avoid scipy/sklearn initialization delays
def get_loader():
    from rag.loader import load_and_split
    return load_and_split

def get_vectorstore_funcs():
    from rag.vectorstore import add_documents, get_document_list, delete_document
    return add_documents, get_document_list, delete_document


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    history: List[dict] = []
    use_rag: bool = True


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    sources: List[dict] = []


class DocumentInfo(BaseModel):
    """Document information model."""
    source: str
    upload_time: str
    chunk_count: int


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    model: str
    vector_count: int
    embedding_model: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    # Create necessary directories
    os.makedirs(os.getenv("UPLOAD_DIR", "./uploads"), exist_ok=True)
    os.makedirs(os.getenv("CHROMA_DB_DIR", "./chroma_db"), exist_ok=True)


# Routes
@app.get("/health", response_model=HealthResponse)
@limiter.limit("30/minute")
async def health(request: Request):
    """Health check endpoint.
    
    Returns status of Ollama connection and vector store stats.
    """
    try:
        from langchain_ollama import ChatOllama
        
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        
        llm = ChatOllama(base_url=ollama_base_url, model=model)
        
        # Test Ollama connection
        try:
            llm.invoke("test")
            status = "ok"
        except:
            status = "ollama_unavailable"
        
        # Count vectors in database (lazy import)
        from rag.vectorstore import get_vectorstore
        vectorstore = get_vectorstore()
        vector_count = vectorstore._collection.count()
        
        return HealthResponse(
            status=status,
            model=model,
            vector_count=vector_count,
            embedding_model=embed_model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """Chat endpoint with streaming response.
    
    Accepts a message and optional conversation history.
    Uses LangGraph to orchestrate the workflow.
    """
    try:
        # Validate input
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create initial state
        state = ChatState(
            message=chat_request.message,
            history=chat_request.history or [],
            use_rag=chat_request.use_rag,
            context=[],
            response="",
            sources=[],
            sanitized=False
        )
        
        # Run through LangGraph workflow
        result_state = run_graph(state)
        
        # Format response
        response = ChatResponse(
            response=result_state["response"],
            sources=result_state.get("sources", [])
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/upload")
@limiter.limit("10/minute")
async def upload(request: Request, file: UploadFile = File(...)):
    """Upload and process a document for RAG.
    
    Supports PDF, TXT, CSV, and DOCX files.
    """
    try:
        # Lazy import
        load_and_split = get_loader()
        add_documents, _, _ = get_vectorstore_funcs()
        
        # Validate file type
        allowed_types = {'.pdf', '.txt', '.csv', '.docx'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_types)}"
            )
        
        # Create upload directory
        upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file temporarily
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Load and split documents
        documents = load_and_split(file_path, file.filename)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No content extracted from file")
        
        # Add to vector store
        add_documents(documents)
        
        # Clean up temporary file
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(documents),
            "message": f"Document uploaded and processed with {len(documents)} chunks"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@app.get("/documents", response_model=List[DocumentInfo])
@limiter.limit("30/minute")
async def list_documents(request: Request):
    """List all uploaded documents in the vector store."""
    try:
        _, get_document_list, _ = get_vectorstore_funcs()
        documents = get_document_list()
        return [DocumentInfo(**doc) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
@limiter.limit("20/minute")
async def delete_doc(request: Request, doc_id: str):
    """Delete a document and its vectors from the vector store.
    
    Args:
        doc_id: The document filename (source) to delete.
    """
    try:
        _, _, delete_document = get_vectorstore_funcs()
        success = delete_document(doc_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
        
        return {
            "status": "success",
            "message": f"Document '{doc_id}' deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )


# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
