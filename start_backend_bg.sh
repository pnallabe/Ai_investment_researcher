#!/bin/bash
# Background startup script for AI Investment Research backend (mvp_simple)

PROJ_DIR="$(dirname "$0")"
cd "$PROJ_DIR"

# Create logs directory if missing
mkdir -p logs

# Kill any process listening on port 8000
pids=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$pids" ]; then
  echo "Killing existing backend processes: $pids"
  kill -9 $pids 2>/dev/null || true
fi

# Start backend with nohup and log output
echo "Starting backend (mvp_simple.py) with logging to logs/backend.log"
nohup python3 mvp_simple.py > logs/backend.log 2>&1 &
BACKEND_PID=$!

echo $BACKEND_PID > logs/backend.pid
sleep 1
if ps -p $BACKEND_PID > /dev/null 2>&1; then
  echo "Backend started (PID: $BACKEND_PID)"
  echo "Logs: $PROJ_DIR/logs/backend.log"
else
  echo "Failed to start backend, check logs: $PROJ_DIR/logs/backend.log"
fi
