#!/usr/bin/env bash

# Complete RAG Demo with GhostAI DLP Firewall
echo "🚀 RAG Demo with GhostAI DLP Firewall"
echo "======================================"
echo ""

# Start Flask app in background
echo "📡 Starting Flask server..."
python app.py &
FLASK_PID=$!

# Wait for server to start
sleep 3

echo "🧪 Testing safe query (should pass)..."
echo "--------------------------------------"
./tests/safe.sh
echo ""

echo "🚨 Testing malicious query (should be blocked)..."
echo "------------------------------------------------"
./tests/malicious.sh
echo ""

echo "📊 Scan results:"
echo "----------------"
if [ -f "scan_results.json" ]; then
    cat scan_results.json | jq
else
    echo "No scan results yet"
fi
echo ""

# Clean up
echo "🛑 Stopping Flask server..."
kill $FLASK_PID 2>/dev/null

echo ""
echo "✅ Demo completed!"
echo "🔒 GhostAI sits inside your RAG stack, scanning every request and blocking data exfiltration attempts before they reach the model — just like a GenAI firewall."
