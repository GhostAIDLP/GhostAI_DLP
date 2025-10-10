#!/usr/bin/env bash

# Test safe query - should be allowed through
echo "🧪 Testing safe query..."
echo ""

curl -s -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Summarize this document about machine learning"}' | jq

echo ""
echo "✅ Safe query completed"
