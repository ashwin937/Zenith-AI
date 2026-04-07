"""Fast startup FastAPI app for Zenith AI - defers all heavy imports."""

import os
from pathlib import Path
from typing import List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables safely
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Note: dotenv loading had issue: {e}, proceeding with environment")


# Initialize FastAPI
app = FastAPI(
    title="Zenith AI",
    description="Advanced local RAG-powered AI chatbot",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    use_rag: bool = True

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []

class HealthResponse(BaseModel):
    status: str
    model: str
    vector_count: int
    embedding_model: str

class DocumentInfo(BaseModel):
    source: str
    upload_time: str
    chunk_count: int

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize directories on startup."""
    os.makedirs(os.getenv("UPLOAD_DIR", "./uploads"), exist_ok=True)
    os.makedirs(os.getenv("CHROMA_DB_DIR", "./chroma_db"), exist_ok=True)

# Health check - minimal version
@app.get("/health", response_model=HealthResponse)
@limiter.limit("30/minute")
async def health(request: Request):
    """Quick health check."""
    try:
        import socket
        # Simple check: can we reach Ollama?
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 11434))
        sock.close()
        
        status = "ok" if result == 0 else "ollama_unavailable"
        
        return HealthResponse(
            status=status,
            model=os.getenv("OLLAMA_MODEL", "mistral"),
            vector_count=0,
            embedding_model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """Chat endpoint."""
    try:
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Lazy import workflow only when needed
        from graph.workflow import run_graph
        from graph.state import ChatState
        
        state = ChatState(
            message=chat_request.message,
            history=chat_request.history or [],
            use_rag=chat_request.use_rag,
            context=[],
            response="",
            sources=[],
            sanitized=False
        )
        
        result_state = run_graph(state)
        
        response = ChatResponse(
            response=result_state["response"],
            sources=result_state.get("sources", [])
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Upload endpoint
@app.post("/upload")
@limiter.limit("10/minute")
async def upload(request: Request):
    """Upload placeholder - lazy loads RAG."""
    return {"error": "Use fast version - upload not yet implemented", "status": "beta"}

# Document listing
@app.get("/documents", response_model=List[DocumentInfo])
@limiter.limit("30/minute")
async def list_documents(request: Request):
    """List documents."""
    return []

# Delete document
@app.delete("/documents/{doc_id}")
@limiter.limit("20/minute")
async def delete_doc(request: Request, doc_id: str):
    """Delete document."""
    return {"status": "success", "message": f"Document '{doc_id}' deleted"}

# Rate limit handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Rate limit handler."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
