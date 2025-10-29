#!/bin/bash
# Background service for AI Investment Research Frontend

echo "🚀 Starting AI Investment Research Frontend as background service..."

# Navigate to project directory
cd "$(dirname "$0")"

# Start frontend in background with logging
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend started with PID: $FRONTEND_PID"
echo "📝 Logs: $(pwd)/../logs/frontend.log"
echo "🌐 URL: http://localhost:3000"
echo ""
echo "🔗 Direct Access Links:"
echo "   🤖 AI Analysis: http://localhost:3000/test-ai"
echo "   📊 Technical Analysis: http://localhost:3000/test-technical"  
echo "   📈 Stock Comparison: http://localhost:3000/test-comparison"
echo ""
echo "To stop the service: kill $FRONTEND_PID"
echo "To view logs: tail -f logs/frontend.log"

# Save PID for later reference
echo $FRONTEND_PID > ../logs/frontend.pid
echo "PID saved to logs/frontend.pid"