#!/bin/bash
# GhostAI Security Firewall - Red Team Daemon Startup Script
# This script starts the algorithmic red teaming system as a background daemon

echo "🤖 Starting GhostAI Red Team Daemon"
echo "===================================="

# Activate virtual environment
source venv_stable/bin/activate

# Check if already running
if pgrep -f "run_continuous_learning.py" > /dev/null; then
    echo "⚠️  Red team daemon is already running!"
    echo "   PID: $(pgrep -f "run_continuous_learning.py")"
    echo "   To restart, run: ./stop_redteam_daemon.sh && ./start_redteam_daemon.sh"
    exit 1
fi

# Create log directory
mkdir -p logs

# Start red team daemon in background
echo "🚀 Starting continuous learning daemon..."
nohup python run_continuous_learning.py \
    --duration 0 \
    --interval 10 \
    --batch-size 5 \
    --daemon \
    > logs/redteam_daemon.log 2>&1 &

# Get PID
REDTEAM_PID=$!

# Wait a moment for startup
sleep 3

# Check if started successfully
if kill -0 $REDTEAM_PID 2>/dev/null; then
    echo "✅ Red team daemon started successfully!"
    echo "   PID: $REDTEAM_PID"
    echo "   Log: logs/redteam_daemon.log"
    echo "   Status: Running continuously"
    echo ""
    echo "📊 To monitor:"
    echo "   tail -f logs/redteam_daemon.log"
    echo "   ./check_redteam_status.sh"
    echo ""
    echo "⏹️  To stop:"
    echo "   ./stop_redteam_daemon.sh"
else
    echo "❌ Failed to start red team daemon!"
    echo "   Check logs/redteam_daemon.log for details"
    exit 1
fi
