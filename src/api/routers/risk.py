from flask import Blueprint, request, jsonify
from api.heuristics import Heuristics
from api.schemas import RiskSyncResponse

bp = Blueprint("risk", __name__)

@bp.route("/risk:sync", methods=["POST"])
def get_sync_risk() -> RiskSyncResponse:
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 400

    res = Heuristics.ENGINE.score(text)
    out = {
        "request_id": payload.get("tenant_id", ""),
        "score": res.score,
        "severity": getattr(res.severity, "value", res.severity),
        "breakdown": [
            {"name": c.name, "score": c.score, "reasons": c.reasons}
            for c in res.breakdown
        ],
        "flags": res.flags,
        "latency_ms": res.latency_ms,
    }
    return jsonify(out), 200

@bp.route("/risk:async", methods=["POST"])
def get_async_risk():
    payload = request.get_json(silent=True) or {}
    return jsonify({"status": "accepted", "request_id": "stub"}), 202
