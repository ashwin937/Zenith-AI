#!/bin/bash

# Kill any existing processes
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "http.server" 2>/dev/null
sleep 1

# Start backend
echo "Starting backend..."
cd "/Users/apple/Desktop/rag project/backend"
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
sleep 3

# Start frontend server
echo "Starting frontend server..."
cd "/Users/apple/Desktop/rag project/frontend"
python3 -c "
import http.server
import socketserver
import os

os.chdir('.')
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(('localhost', 8080), Handler) as httpd:
    print('Frontend server running on http://localhost:8080')
    httpd.serve_forever()
" &
FRONTEND_PID=$!
sleep 2

# Open in browser
echo "Opening browser..."
open http://localhost:8080

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
