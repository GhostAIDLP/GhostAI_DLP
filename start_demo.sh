#!/bin/bash
# GhostAI firewall Demo Startup Script

echo "🚀 Starting GhostAI firewall Demo"
echo "=============================="

# Activate virtual environment
source venv_stable/bin/activate

# Start Mock LLM Server in background
echo "🤖 Starting Mock LLM Server..."
python mock_llm_server.py &
MOCK_PID=$!

# Wait a moment for mock server to start
sleep 2

# Start Proxy in background  
echo "🌐 Starting firewall Proxy..."
python run_proxy.py &
PROXY_PID=$!

# Wait a moment for proxy to start
sleep 3

# Start Dashboard in background
echo "📊 Starting Dashboard..."
streamlit run dashboard_simple.py &
DASHBOARD_PID=$!

# Wait for services to start
sleep 5

echo ""
echo "✅ All services started!"
echo "=============================="
echo "📍 Mock LLM: http://localhost:5005"
echo "📍 firewall Proxy: http://localhost:5004" 
echo "📍 Dashboard: http://localhost:8501"
echo ""
echo "🧪 Run demo: python demo_features.py"
echo "⏹️  Stop all: ./stop_demo.sh"
echo ""

# Keep script running
echo "Press Ctrl+C to stop all services..."
trap 'echo "Stopping services..."; kill $MOCK_PID $PROXY_PID $DASHBOARD_PID; exit' INT
wait
