from flask import Flask, request, jsonify
from api.heuristics import Heuristics  # the singleton you built above

app = Flask(__name__)

@app.route("/risk:sync", methods=["POST"])
def get_sync_risk():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 400

    res = Heuristics.ENGINE.score(text)  # HeuristicsResult dataclass or dict
    # If it's a dataclass, convert to dict (depends on your implementation)
    out = {
        "score": res.score,
        "severity": res.severity.value if hasattr(res.severity, "value") else res.severity,
        "breakdown": [{"name": c.name, "score": c.score, "reasons": c.reasons} for c in res.breakdown],
        "flags": res.flags,
        "latency_ms": res.latency_ms,
    }
    return jsonify(out), 200

@app.route("/risk:async", methods=["POST"])
def get_async_risk():
    # Day-1 stub: accept but don’t enqueue yet
    payload = request.get_json(silent=True) or {}
    return jsonify({"status": "accepted", "request_id": "stub"}), 202

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")