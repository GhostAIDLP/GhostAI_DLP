#!/bin/bash
# GhostAI Security Firewall Demo Startup Script

echo "🔥 Starting GhostAI Security Firewall Demo"
echo "=========================================="

# Activate virtual environment
source venv_stable/bin/activate

# Start Mock LLM Server in background
echo "🤖 Starting Mock LLM Server..."
python mock_llm_server.py &
MOCK_PID=$!

# Wait a moment for mock server to start
sleep 2

# Start Security Firewall in background  
echo "🔥 Starting Security Firewall..."
python run_firewall.py --mock --mode=firewall &
FIREWALL_PID=$!

# Wait a moment for firewall to start
sleep 3

# Start Dashboard in background
echo "📊 Starting Dashboard..."
streamlit run dashboard_simple.py &
DASHBOARD_PID=$!

# Wait for services to start
sleep 5

echo ""
echo "✅ All services started!"
echo "=========================================="
echo "📍 Mock LLM: http://localhost:5005"
echo "🔥 Security Firewall: http://localhost:5004" 
echo "📊 Dashboard: http://localhost:8501"
echo ""
echo "🧪 Run firewall demo: python demo_firewall.py"
echo "📊 Firewall stats: curl http://localhost:5004/firewall/stats"
echo "⏹️  Stop all: ./stop_demo.sh"
echo ""

# Test firewall health
echo "🔍 Testing firewall health..."
curl -s http://localhost:5004/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Firewall is healthy and ready!"
else
    echo "❌ Firewall health check failed"
fi

# Keep script running
echo "Press Ctrl+C to stop all services..."
trap 'echo "Stopping services..."; kill $MOCK_PID $FIREWALL_PID $DASHBOARD_PID; exit' INT
wait
