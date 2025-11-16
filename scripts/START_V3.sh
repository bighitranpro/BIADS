#!/bin/bash
# Bi Ads Multi Tool PRO v3.0 - Startup Script
# This script helps you start the application

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║            🚀 Bi Ads Multi Tool PRO v3.0 - Startup Script                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"
echo ""

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    echo "Please run this script from the webapp directory."
    exit 1
fi

# Function to check if Python dependencies are installed
check_python_deps() {
    echo "🔍 Checking Python dependencies..."
    if python3 -c "import fastapi" 2>/dev/null; then
        echo "✅ Python dependencies are installed"
        return 0
    else
        echo "⚠️  Python dependencies not installed"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    echo ""
    echo "📦 Installing Python dependencies..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check if venv exists
    if [ ! -d "backend/venv" ]; then
        echo "📦 Creating virtual environment..."
        cd backend
        python3 -m venv venv
        cd ..
    fi
    
    # Activate venv and install
    echo "📦 Installing packages in virtual environment..."
    cd backend
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    
    echo "✅ Python dependencies installed successfully!"
}

# Function to check if .env exists
check_env_file() {
    echo ""
    echo "🔍 Checking environment configuration..."
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found!"
        echo "📝 Creating .env from template..."
        cp .env.example .env
        echo "✅ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env file with your credentials:"
        echo "   - FACEBOOK_APP_ID"
        echo "   - FACEBOOK_APP_SECRET"
        echo "   - FACEBOOK_VERIFY_TOKEN"
        echo "   - TELEGRAM_BOT_TOKEN"
        echo "   - TELEGRAM_CHAT_ID"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "✅ .env file exists"
    fi
}

# Function to start backend
start_backend() {
    echo ""
    echo "🚀 Starting Backend Server..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cd backend
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo "📡 API: http://localhost:8000"
    echo "📖 Docs: http://localhost:8000/docs"
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to initialize..."
    sleep 3
}

# Function to start frontend
start_frontend() {
    echo ""
    echo "🚀 Starting Frontend Application..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    
    npm start &
    FRONTEND_PID=$!
    
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
}

# Main execution
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check and install dependencies
if ! check_python_deps; then
    read -p "Install Python dependencies now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_python_deps
    else
        echo "❌ Cannot start without dependencies. Exiting."
        exit 1
    fi
fi

# Check .env file
check_env_file

# Start services
echo ""
echo "🚀 Starting Bi Ads Multi Tool PRO v3.0..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

start_backend
start_frontend

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ Bi Ads Multi Tool PRO v3.0 Running                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Application URLs:"
echo "   • Frontend: Electron app window"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Features Available:"
echo "   • Facebook Webhook Integration"
echo "   • Telegram Bot Notifications"
echo "   • Settings Management"
echo "   • Plugin System"
echo "   • Help & Documentation"
echo ""
echo "🔧 To stop the application:"
echo "   Press Ctrl+C in this terminal"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Stopped'; exit 0" INT TERM

# Keep script running
wait
