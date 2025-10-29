#!/bin/bash
# AI Investment Research - Service Management

PROJ_DIR="/Users/swarnabale/Documents/My Projects/Ai_investment_researcher"
PID_FILE="$PROJ_DIR/logs/frontend.pid"
LOG_FILE="$PROJ_DIR/logs/frontend.log"

case "$1" in
    start)
        echo "🚀 Starting AI Investment Research Frontend..."
        cd "$PROJ_DIR" && ./start_frontend_bg.sh
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            echo "🛑 Stopping frontend service (PID: $PID)..."
            kill $PID 2>/dev/null
            rm -f "$PID_FILE"
            echo "✅ Frontend service stopped"
        else
            echo "❌ No PID file found - service may not be running"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "✅ Frontend service is running (PID: $PID)"
                echo "🌐 Available at: http://localhost:3000"
                echo "🔗 Direct links:"
                echo "   🤖 AI Analysis: http://localhost:3000/test-ai"
                echo "   📊 Technical: http://localhost:3000/test-technical"
                echo "   📈 Comparison: http://localhost:3000/test-comparison"
            else
                echo "❌ Frontend service is not running (stale PID file)"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ Frontend service is not running"
        fi
        ;;
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo "📝 Frontend logs:"
            tail -f "$LOG_FILE"
        else
            echo "❌ No log file found"
        fi
        ;;
    *)
        echo "🎯 AI Investment Research - Service Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the frontend service"
        echo "  stop    - Stop the frontend service"  
        echo "  restart - Restart the frontend service"
        echo "  status  - Check service status"
        echo "  logs    - View real-time logs"
        echo ""
        exit 1
        ;;
esac