#!/bin/bash
# Frontend startup script for AI Investment Research

echo "🚀 Starting AI Investment Research Frontend..."
echo "📁 Working directory: $(pwd)"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Kill any existing processes on port 3000
echo "🧹 Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "No processes to kill on port 3000"

# Start the development server
echo "🌐 Starting Vite development server..."
echo "✅ Frontend will be available at: http://localhost:3000"
echo "🔗 Direct AI Analysis: http://localhost:3000/test-ai"
echo "📊 Technical Analysis: http://localhost:3000/test-technical"
echo "📈 Stock Comparison: http://localhost:3000/test-comparison"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start with output
npm run dev
