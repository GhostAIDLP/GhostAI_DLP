# RAG Demo with GhostAI firewall Firewall

A minimal Flask-based RAG demo that integrates the GhostAI firewall SDK as a middleware "firewall" to protect against data exfiltration attempts.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Flask server:
   ```bash
   ./run.sh
   ```

3. Test the demo:
   ```bash
   # Test safe query (should pass)
   ./tests/safe.sh
   
   # Test malicious query (should be blocked)
   ./tests/malicious.sh
   ```

4. Check scan results:
   ```bash
   cat scan_results.json | jq
   ```

## How It Works

- **GhostAI firewall** scans every incoming query for sensitive data patterns
- **Safe queries** (like document summarization) pass through with low risk scores
- **Malicious queries** (like API key exfiltration) are blocked with high risk scores
- **All scans** are logged to `scan_results.json` with timestamps and risk scores

## Demo Flow

1. Flask app starts with GhostAI firewall protection active
2. Safe query returns LLM response with low risk score
3. Malicious query returns 403 error with high risk score
4. Scan results show the protection in action

**GhostAI sits inside your RAG stack, scanning every request and blocking data exfiltration attempts before they reach the model — just like a GenAI firewall.**
