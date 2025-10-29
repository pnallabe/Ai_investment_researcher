#!/bin/bash

# AI Investment Research Bot - MVP Startup Script
# This script demonstrates the complete system setup and startup

echo "🚀 AI Investment Research Bot - MVP Setup & Demo"
echo "=================================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cat > .env << EOF
# Environment
ENV=development
DEBUG=true

# Server
HOST=localhost
PORT=8000

# Database URLs (Update with your actual database credentials)
DATABASE_URL=postgresql://user:password@localhost:5432/investment_research
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379/0

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001

# API Keys (Add your actual API keys)
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here

# Security
SECRET_KEY=super-secret-key-change-in-production-make-it-very-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT=100

# AI/NLP Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_TOKENS=4000
TEMPERATURE=0.7
EOF
    echo "✅ Created .env file with default settings"
    echo "⚠️  Please update the API keys and database credentials in .env file"
fi

echo ""
echo "🎯 MVP Components Status:"
echo "========================"
echo "✅ Project Structure & Configuration"
echo "✅ Data Ingestion Layer (SEC EDGAR, News, Market Data)"
echo "✅ Database Models (PostgreSQL, Neo4j, ChromaDB)"
echo "✅ Analytics Engine (Financial Metrics, Forecasting)"
echo "✅ AI/NLP Layer with RAG System"
echo "✅ FastAPI Backend Services"
echo "   - Authentication & Authorization (JWT)"
echo "   - Research Query API with RAG"
echo "   - Company Analysis Endpoints"
echo "   - Portfolio Management API"
echo "   - Data Management Interface"
echo "   - Analytics & Forecasting API"
echo "   - WebSocket for Real-time Features"
echo "🔄 React Frontend (Next phase)"
echo "🔄 Monitoring & Security (Next phase)"

echo ""
echo "🌐 API Endpoints Available:"
echo "=========================="
echo "Authentication:"
echo "  POST /v1/auth/register     - User registration"
echo "  POST /v1/auth/login        - User login"
echo "  GET  /v1/auth/me           - Current user info"
echo ""
echo "Research Queries:"
echo "  POST /v1/research/query    - Execute AI research query"
echo "  GET  /v1/research/history  - Query history"
echo "  GET  /v1/research/suggestions - Query suggestions"
echo ""
echo "Company Analysis:"
echo "  GET  /v1/company/{ticker}/summary    - Company summary"
echo "  GET  /v1/company/{ticker}/metrics    - Financial metrics"
echo "  GET  /v1/company/{ticker}/analysis   - Complete analysis"
echo "  POST /v1/company/{ticker}/forecast   - Price forecast"
echo ""
echo "Portfolio Management:"
echo "  GET  /v1/portfolio/                  - User portfolios"
echo "  POST /v1/portfolio/                 - Create portfolio"
echo "  GET  /v1/portfolio/{id}             - Portfolio details"
echo "  POST /v1/portfolio/{id}/holdings    - Add holding"
echo "  POST /v1/portfolio/{id}/scenario    - Scenario analysis"
echo ""
echo "Data & Analytics:"
echo "  GET  /v1/data/sources               - Data source status"
echo "  POST /v1/data/ingest/{type}        - Trigger ingestion"
echo "  GET  /v1/analytics/market           - Market analysis"
echo ""
echo "Real-time Features:"
echo "  WebSocket /ws/chat                  - Real-time research chat"
echo "  WebSocket /ws/market-data           - Live market data"
echo ""
echo "Documentation:"
echo "  GET  /docs                          - Interactive API docs"
echo "  GET  /redoc                         - ReDoc documentation"

echo ""
echo "🚀 Starting the AI Investment Research Bot MVP..."
echo "================================================"

# Check if we want to run in standalone mode
if [ "$1" = "standalone" ]; then
    echo "🔧 Running in standalone mode (services only, no web API)..."
    python main.py standalone
else
    echo "🌐 Starting FastAPI web server..."
    echo "📝 Access the API documentation at: http://localhost:8000/docs"
    echo "🔍 Alternative docs at: http://localhost:8000/redoc"
    echo "❤️  Health check at: http://localhost:8000/health"
    echo ""
    echo "🛑 Press Ctrl+C to stop the server"
    echo ""
    
    # Start the FastAPI server
    python main.py
fi