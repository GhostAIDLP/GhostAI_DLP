#!/bin/bash
# GhostAI firewall Demo Stop Script

echo "⏹️  Stopping GhostAI firewall Demo Services"
echo "======================================"

# Kill processes by port
echo "🛑 Stopping services..."

# Kill by port 5004 (proxy)
lsof -ti:5004 | xargs kill -9 2>/dev/null || echo "No process on port 5004"

# Kill by port 5005 (mock LLM)  
lsof -ti:5005 | xargs kill -9 2>/dev/null || echo "No process on port 5005"

# Kill by port 8501 (dashboard)
lsof -ti:8501 | xargs kill -9 2>/dev/null || echo "No process on port 8501"

echo "✅ All services stopped!"
