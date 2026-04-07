#!/bin/bash
# SecureChat AI - Startup Script
# Run this script to start the complete application

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 SecureChat AI - Startup Script"
echo "=================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ required, found $PYTHON_VERSION"
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check Ollama
echo "🤖 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found in PATH"
    echo "Download from: https://ollama.ai"
    echo "After installing, run: ollama serve"
    exit 1
fi
echo "✅ Ollama found"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running"
    echo "Starting Ollama... (open in new terminal)"
    echo "Run: ollama serve"
    echo ""
    echo "Once Ollama is running, press Enter to continue..."
    read
fi

if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "❌ Still cannot connect to Ollama"
    exit 1
fi
echo "✅ Ollama is running"
echo ""

# Check models
echo "📥 Checking Ollama models..."
if ! ollama list | grep -q "llama2"; then
    echo "⚠️  llama2 model not found, pulling..."
    ollama pull llama2
fi
if ! ollama list | grep -q "nomic-embed-text"; then
    echo "⚠️  nomic-embed-text model not found, pulling..."
    ollama pull nomic-embed-text
fi
echo "✅ Models available"
echo ""

# Setup backend
echo "🔧 Setting up backend..."
cd "$PROJECT_DIR/backend"

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python packages..."
pip install -q -r requirements.txt

echo "✅ Backend ready"
echo ""

# Create directories
mkdir -p uploads
mkdir -p chroma_db

# Start backend
echo "🚀 Starting FastAPI backend..."
echo "Backend will run on: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

# Open frontend in browser (macOS)
if command -v open &> /dev/null; then
    echo "🌐 Opening frontend in browser..."
    open "$PROJECT_DIR/frontend/index.html"
fi

# Run backend
cd "$PROJECT_DIR/backend"
uvicorn main:app --reload --port 8000
