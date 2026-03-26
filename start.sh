#!/bin/bash

# Aggressive Inline Trick Generator - Startup Script
# This script starts the Flask API backend and opens the web app

echo "🛼 Aggressive Inline Trick Generator"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start Flask API
echo ""
echo "🚀 Starting Flask API server..."
echo "   API will be available at: http://localhost:5000"
echo ""
echo "📝 To use the app:"
echo "   1. Keep this terminal open (API is running)"
echo "   2. Open sports/rollerblading/app.html in your browser"
echo "   3. Or run: python3 -m http.server 8000 (in another terminal)"
echo "      Then visit: http://localhost:8000/sports/rollerblading/app.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "===================================="
echo ""

# Run Flask API
cd sports && python3 trick_api.py
