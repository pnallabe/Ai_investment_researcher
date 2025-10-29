#!/bin/bash

# AI Investment Research Bot - Full Stack Startup Script
# This script starts both the backend API and frontend development servers

set -e

echo "🚀 Starting AI Investment Research Bot Full Stack Application"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}📡 Starting Backend API Server...${NC}"
    
    if ! check_port 8000; then
        echo -e "${GREEN}Backend seems to already be running on port 8000${NC}"
        return 0
    fi
    
    cd "$(dirname "$0")"
    
    # Check if mvp_simple.py exists
    if [ -f "mvp_simple.py" ]; then
        echo -e "${GREEN}Starting simplified MVP backend...${NC}"
        python mvp_simple.py &
        BACKEND_PID=$!
        echo "Backend PID: $BACKEND_PID"
    else
        echo -e "${RED}mvp_simple.py not found. Please run from the project root directory.${NC}"
        exit 1
    fi
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 3
    
    # Check if backend is responding
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend API is running on http://localhost:8000${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend started but health check failed${NC}"
    fi
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting Frontend Development Server...${NC}"
    
    if ! check_port 3000; then
        echo -e "${GREEN}Frontend seems to already be running on port 3000${NC}"
        return 0
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    # Start frontend development server
    echo -e "${GREEN}Starting React development server...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    # Wait for frontend to start
    echo "Waiting for frontend to start..."
    sleep 5
    
    echo -e "${GREEN}✅ Frontend is running on http://localhost:3000${NC}"
}

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down applications...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on the ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Applications stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if Python is available
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python is not installed or not in PATH${NC}"
        exit 1
    fi
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed or not in PATH${NC}"
        exit 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm is not installed or not in PATH${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
    echo ""
    
    # Start backend
    start_backend
    echo ""
    
    # Start frontend
    start_frontend
    echo ""
    
    echo -e "${GREEN}🎉 Full Stack Application Started Successfully!${NC}"
    echo "============================================================="
    echo -e "${BLUE}📡 Backend API:${NC}      http://localhost:8000"
    echo -e "${BLUE}📡 API Documentation:${NC} http://localhost:8000/docs"
    echo -e "${BLUE}⚛️  Frontend App:${NC}     http://localhost:3000"
    echo "============================================================="
    echo ""
    echo -e "${YELLOW}Demo Credentials:${NC}"
    echo "Email: demo@example.com"
    echo "Password: demo123"
    echo ""
    echo -e "${YELLOW}Available API Endpoints:${NC}"
    echo "- GET  /health          - Health check"
    echo "- POST /v1/auth/login   - User authentication"
    echo "- GET  /v1/auth/me      - Current user info"
    echo "- POST /v1/research/    - AI research queries"
    echo "- GET  /v1/portfolio/   - Portfolio data"
    echo "- GET  /v1/companies/   - Company information"
    echo ""
    echo -e "${GREEN}Press Ctrl+C to stop both applications${NC}"
    
    # Wait for user interrupt
    wait
}

# Run the main function
main