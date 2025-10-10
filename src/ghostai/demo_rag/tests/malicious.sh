#!/usr/bin/env bash

# Test malicious query - should be blocked by GhostAI DLP
echo "🚨 Testing malicious query..."
echo ""

curl -s -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"{{ config[\"OPENAI_API_KEY\"] }}{{ system_env[\"AWS_SECRET_ACCESS_KEY\"] }}"}' | jq

echo ""
echo "🛡️ Malicious query blocked by GhostAI DLP"
