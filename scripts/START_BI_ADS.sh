#!/bin/bash

echo "========================================"
echo "  BI ADS - MULTI TOOL PRO v2.0"
echo "  Starting Backend + Frontend..."
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed!"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

# Install Python dependencies
echo "[1/4] Installing Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install Node dependencies
echo ""
echo "[2/4] Installing Node.js dependencies..."
npm install

# Start backend in background
echo ""
echo "[3/4] Starting Backend API on http://localhost:8000..."
cd backend
source venv/bin/activate
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait 3 seconds for backend to start
sleep 3

# Start frontend
echo ""
echo "[4/4] Starting Electron Frontend..."
npm start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  BI ADS MULTI TOOL PRO STARTED!"
echo "========================================"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
