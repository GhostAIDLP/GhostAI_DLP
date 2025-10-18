#!/bin/bash
# GhostAI Security Firewall - Red Team Daemon Stop Script

echo "🛑 Stopping GhostAI Red Team Daemon"
echo "==================================="

# Find and kill red team processes
REDTEAM_PIDS=$(pgrep -f "run_continuous_learning.py")

if [ -z "$REDTEAM_PIDS" ]; then
    echo "ℹ️  No red team daemon processes found"
    exit 0
fi

echo "🔍 Found red team processes: $REDTEAM_PIDS"

# Kill processes
for pid in $REDTEAM_PIDS; do
    echo "🔄 Stopping process $pid..."
    kill $pid
    
    # Wait for graceful shutdown
    sleep 2
    
    # Force kill if still running
    if kill -0 $pid 2>/dev/null; then
        echo "⚡ Force stopping process $pid..."
        kill -9 $pid
    fi
done

# Verify shutdown
sleep 1
if pgrep -f "run_continuous_learning.py" > /dev/null; then
    echo "❌ Some processes may still be running"
    echo "   Run: pkill -9 -f 'run_continuous_learning.py'"
else
    echo "✅ Red team daemon stopped successfully"
fi
