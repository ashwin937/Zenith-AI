#!/bin/bash

# 🚀 Zenith AI - Startup Script
# Advanced Local RAG Chatbot

echo ""
echo "╔════════════════════════════════════════╗"
echo "║      🚀 ZENITH AI - Startup 🚀        ║"
echo "║   Advanced Local RAG Chatbot          ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Kill any existing processes
echo "🧹 Cleaning up old processes..."
pkill -f "uvicorn main:app" 2>/dev/null
sleep 1

# Change to backend directory
cd "/Users/apple/Desktop/zenith-ai/backend" || exit 1

# Verify .env is configured
echo "✅ Configuration Check"
MODEL=$(grep "OLLAMA_MODEL" .env | cut -d= -f2)
echo "   Model: $MODEL"
echo "   Embeddings: nomic-embed-text"
echo "   Database: ChromaDB"

# Verify Ollama
echo ""
echo "✅ Ollama Service Check"
curl -s http://localhost:11434 > /dev/null
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✓${NC} Ollama is running on localhost:11434"
else
    echo -e "   ${RED}✗${NC} Ollama not running"
    echo "   Please start Ollama first: ollama serve"
    exit 1
fi

# Verify Model
echo ""
echo "✅ Model Check"
ollama list | grep "$MODEL" > /dev/null
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✓${NC} $MODEL model is installed"
else
    echo -e "   ${RED}✗${NC} $MODEL not found"
    exit 1
fi

# Start backend
echo ""
echo "🚀 Starting Zenith AI Backend..."
echo "   FastAPI on: localhost:8000"
echo "   LLM: $MODEL"
echo "   Features: Math tools, RAG, Document Q&A"
echo ""

python3 -m uvicorn main:app --host localhost --port 8000

echo ""
echo "╔════════════════════════════════════════╗"
echo "║       ✅ ZENITH AI STARTED ✅         ║"
echo "║  Open: http://localhost:8000         ║"
echo "║  Press Ctrl+C to stop                ║"
echo "╚════════════════════════════════════════╝"
