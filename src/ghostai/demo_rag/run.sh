#!/usr/bin/env bash

# RAG Demo with GhostAI DLP Firewall
echo "🚀 Starting RAG Demo with GhostAI DLP Firewall"
echo "📊 Scan results will be logged to scan_results.json"
echo "🔒 GhostAI is protecting against data exfiltration"
echo ""

export FLASK_APP=app.py
export FLASK_ENV=development
python app.py
