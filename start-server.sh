#!/bin/bash

# Quick Start Script - Aggressive Inline Trick Generator
# This script launches a local web server to test the app

echo "🛼 Starting Aggressive Inline Trick Generator..."
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✓ Using Python 3"
    echo "🌐 Opening http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python3 -m http.server 8000
# Check if Python 2 is available
elif command -v python &> /dev/null; then
    echo "✓ Using Python 2"
    echo "🌐 Opening http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python -m SimpleHTTPServer 8000
# Check if Node.js http-server is available
elif command -v http-server &> /dev/null; then
    echo "✓ Using http-server (Node.js)"
    echo "🌐 Opening http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    http-server -p 8000
else
    echo "❌ No web server found!"
    echo ""
    echo "Please install one of the following:"
    echo "  - Python 3: sudo apt install python3"
    echo "  - Node.js: npm install -g http-server"
    echo ""
    echo "Or open index.html in your browser (may not work due to CORS)"
    exit 1
fi
