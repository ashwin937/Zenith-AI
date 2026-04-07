# Zenith AI - Advanced Local RAG Chatbot

A complete, production-ready full-stack chatbot with Retrieval-Augmented Generation (RAG), 
powered by Mistral, Ollama, LangChain, LangGraph, and ChromaDB. Zero external API calls, zero API keys required.

## 🎯 Features

✨ **Advanced AI Capabilities**
- Local LLM via Mistral (optimized with sliding window attention)
- Integrated math calculator tool for accurate calculations
- Retrieval-Augmented Generation (RAG) for document Q&A
- Chat history and conversation management
- Source document citations

🔒 **Privacy & Security**
- 100% local - no cloud APIs
- No API keys required
- Offline-first design
- Secure document handling

⚡ **Performance**
- Optimized Mistral with sliding window attention
- Fast inference (~3-8 seconds)
- Batch processing optimization
- Reduced token generation (256 max)

🎨 **Beautiful UI**
- Dark glassmorphism theme
- Responsive design (mobile + desktop)
- Markdown rendering with syntax highlighting
- Animated chat bubbles
- RAG toggle switch

📚 **RAG Features**
- Document upload (PDF, TXT, CSV, DOCX)
- ChromaDB vector database
- Similarity search (k=2)
- Metadata tracking
- Document management

## 🚀 Quick Start

### 1. Prerequisites
- Ollama running locally
- Python 3.13+
- Mistral model downloaded

### 2. Install Dependencies
```bash
cd zenith-ai/backend
pip install -r requirements.txt
```

### 3. Start Backend
```bash
python3 -m uvicorn main:app --host localhost --port 8000
```

### 4. Open Frontend
Open browser: **http://localhost:8000**

## 📦 What's Included

```
zenith-ai/
├── frontend/index.html      (Complete UI - 1,200 lines)
├── backend/
│   ├── main.py              (FastAPI - 285 lines)
│   ├── rag/                 (RAG modules - 295 lines)
│   │   ├── math_tools.py    (Calculator integration)
│   │   ├── chain.py         (LangChain RAG)
│   │   ├── loader.py        (Document loaders)
│   │   └── vectorstore.py   (ChromaDB operations)
│   ├── graph/               (LangGraph - 170 lines)
│   │   ├── workflow.py      (5-node orchestration)
│   │   └── state.py         (State management)
│   └── requirements.txt
└── README.md
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Backend | FastAPI + Uvicorn |
| LLM | Mistral (via Ollama) |
| Embeddings | nomic-embed-text |
| Vector DB | ChromaDB |
| Orchestration | LangGraph |
| RAG Framework | LangChain |
| Math Tools | Integrated Calculator |

## 📋 API Endpoints

- **POST /chat** - Send message and get response
- **POST /upload** - Upload documents
- **GET /documents** - List uploaded documents
- **DELETE /documents/{doc_id}** - Remove document
- **GET /health** - Health check

## ⚙️ Configuration

Edit `.env` file:
```properties
OLLAMA_MODEL=mistral
OLLAMA_EMBED_MODEL=nomic-embed-text
SIMILARITY_K=2
CHUNK_OVERLAP=50
RATE_LIMIT=20
```

## �� Features in Action

### Math Calculations
```
You: "What is 12345 × 6789?"
Zenith AI: Uses calculator tool → 83810205
```

### Document Q&A
```
You: Upload PDF → Ask about it with RAG ON
Zenith AI: Retrieves context → Answers with source citations
```

### Smart Reasoning
```
You: "Calculate 2^10 and show your work"
Zenith AI: Shows step-by-step calculation using math tool
```

## 📊 Performance

| Operation | Time |
|-----------|------|
| Page load | <1s |
| First response | 30-40s |
| Subsequent responses | 3-8s |
| Math calculation | <500ms |
| Document search | <100ms |

## 🔄 Data Flow

1. User sends message via frontend
2. Backend validates input
3. LangGraph workflow processes:
   - Input sanitization
   - RAG decision routing
   - Context retrieval (if RAG enabled)
   - LLM response generation
   - Output formatting
4. Response with citations returned
5. Frontend displays with markdown rendering

## 🛡️ Security Features

- Input sanitization (removes control chars)
- Rate limiting (20 requests/minute)
- File validation (only approved types)
- No sensitive data logging
- Optional password protection

## 🎓 Learning Path

1. **Basics** - Chat with LLM
2. **Math** - Try calculations
3. **Documents** - Upload and ask
4. **Advanced** - Modify prompts and settings
5. **Development** - Customize code

## 📱 System Requirements

- macOS / Linux / Windows
- Python 3.13+
- 8GB RAM (minimum)
- 10GB disk (for models)
- Ollama installed and running

## 🤝 Contributing

This is a complete project. Feel free to:
- Modify the UI
- Add new document types
- Integrate additional tools
- Customize the LLM prompts
- Deploy to production

## 📄 License

MIT License - Free for personal and commercial use

---

**Zenith AI** - Where Local AI Reaches Its Peak 🚀

Built with ❤️ for privacy-first AI
