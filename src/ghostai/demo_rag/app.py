from flask import Flask, request, jsonify
from ghostai import Pipeline
import json
import os
import datetime

app = Flask(__name__)
pipeline = Pipeline()

def log_result(text, result):
    """Log scan results to scan_results.json"""
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "prompt_excerpt": text[:60],
        "risk_score": result["score"],
        "flags": result["flags"]
    }
    with open("scan_results.json", "a") as f:
        f.write(json.dumps(record) + "\n")

@app.route("/query", methods=["POST"])
def query():
    """Main RAG query endpoint with GhostAI DLP protection"""
    data = request.get_json()
    query_text = data.get("query", "")
    
    # Scan the query with GhostAI DLP
    result = pipeline.run(query_text)
    log_result(query_text, result)

    # Block if risk score is too high
    if result["score"] > 0.8:
        return jsonify({
            "error": "Prompt blocked by GhostAI DLP",
            "risk_score": result["score"],
            "flags": result["flags"]
        }), 403

    # Allow safe queries to proceed
    return jsonify({
        "answer": f"LLM output for: {query_text}",
        "risk_score": result["score"],
        "flags": result["flags"]
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "ghostai": "active"})

if __name__ == "__main__":
    # Initialize empty scan results file
    if not os.path.exists("scan_results.json"):
        with open("scan_results.json", "w") as f:
            f.write("")
    
    print("🚀 Starting RAG Demo with GhostAI DLP Firewall")
    print("📊 Scan results will be logged to scan_results.json")
    print("🔒 GhostAI is protecting against data exfiltration")
    app.run(host="0.0.0.0", port=5000, debug=True)
