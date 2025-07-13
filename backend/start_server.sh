#!/bin/bash

# Kill any existing uvicorn processes
echo "Stopping any existing uvicorn processes..."
pkill -f uvicorn 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if port 8000 is free
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8000 is still in use. Trying port 8001..."
    PORT=8001
else
    PORT=8000
fi

echo "Starting uvicorn server on port $PORT..."
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

# Start the server
uvicorn main:app --reload --port $PORT --host 0.0.0.0 