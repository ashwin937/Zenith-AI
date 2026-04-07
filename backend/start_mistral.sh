#!/bin/bash

# Startup script for SecureChat AI with Mistral

echo "🚀 Starting SecureChat AI with Mistral..."
echo ""

# Kill any existing processes
echo "Cleaning up old processes..."
pkill -f "uvicorn main:app" 2>/dev/null
sleep 1

# Change to backend directory
cd "/Users/apple/Desktop/rag\ project/backend" || exit 1

# Verify .env is configured for Mistral
echo "✅ Checking configuration..."
MODEL=$(grep "OLLAMA_MODEL" .env | cut -d= -f2)
echo "   Model: $MODEL"

# Verify Mistral is installed
echo "✅ Checking Mistral..."
ollama list | grep mistral > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Mistral is installed"
else
    echo "   ❌ Mistral not found. Installing..."
    ollama pull mistral
fi

# Verify Ollama is running
echo "✅ Checking Ollama service..."
curl -s http://localhost:11434 > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Ollama is running"
else
    echo "   ❌ Ollama not running. Please start Ollama first."
    exit 1
fi

# Start the backend
echo ""
echo "🚀 Starting FastAPI backend..."
python3 -m uvicorn main:app --host localhost --port 8000 --reload

echo ""
echo "✅ Backend started!"
echo "📱 Open browser: http://localhost:8000"
echo "🔧 Model: $MODEL"
echo "📊 Math tools: Enabled"
echo ""
echo "Press Ctrl+C to stop"
