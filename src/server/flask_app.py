# from flask import Flask, request, jsonify
# from policy import apply_policies
# from normalize import normalize as normalize_findings

# app = Flask(__name__)

# @app.get("/health")
# def health():
#     return jsonify({"ok": True, "service": "ghostai-mcp", "version": "0.1.0"})

# @app.post("/normalize")
# def route_normalize():
#     """
#     Body:
#     {
#       "results": [ { "name": "...", "flagged": true, "score": 4.9, "reasons": ["..."], "extra": {...} }, ... ]
#     }
#     Returns: findings[] in your unified schema
#     """
#     data = request.get_json(force=True) or {}
#     results = data.get("results", [])
#     # If your scanners output raw JSON (not ScanResult), make an adapter here.
#     findings = normalize_findings(results)  # or adapter_then_normalize(results)
#     return jsonify({"findings": findings})

# @app.post("/evaluate")
# def route_evaluate():
#     """
#     Body:
#     {
#       "findings": [ ... normalized ... ],
#       "rules": [
#         {"id":"block_high_entropy_in_src",
#          "if": 'detector in ["gitleaks","trufflehog"] and score > 4.5 and LIKE(file_path, "src/**")',
#          "action": "block",
#          "reason": "High entropy token in app code"}
#       ],
#       "thresholds": [
#         {"id":"too_many_tokens_in_file", "scope":"per_file",
#          "if": 'detector in ["gitleaks","trufflehog"] and score > 4.5',
#          "count_gte": 5, "action":"block", "reason":">5 tokens in a single file"}
#       ]
#     }
#     Returns: { decisions: [...], status: "block|warn|ok", summary: {...} }
#     """
#     data = request.get_json(force=True) or {}
#     findings = data.get("findings", [])
#     rules = data.get("rules", [])
#     thresholds = data.get("thresholds", [])

#     decisions = apply_policies(findings, rules)

#     # naive thresholding (per_file / per_pr)
#     status = "ok"
#     summary = {"block": 0, "warn": 0, "log": 0, "error": 0}
#     for d in decisions:
#         summary[d["action"]] = summary.get(d["action"], 0) + 1

#     # apply thresholds
#     from collections import defaultdict
#     per_file_counts = defaultdict(int)
#     for f in findings:
#         if f.get("file_path"):
#             per_file_counts[f["file_path"]] += 1

#     for th in thresholds:
#         if th.get("scope") == "per_file":
#             # filter findings that match 'if'
#             from policies.engine import safe_eval
#             for file_path, _ in per_file_counts.items():
#                 count = sum(
#                     1 for f in findings
#                     if f.get("file_path") == file_path and safe_eval(th.get("if", "False"), {**f, **f.get("extra", {})})
#                 )
#                 if count >= int(th.get("count_gte", 0)):
#                     decisions.append({
#                         "finding": {"file_path": file_path},
#                         "rule_id": th["id"],
#                         "action": th["action"],
#                         "reason": th.get("reason")
#                     })
#                     summary[th["action"]] = summary.get(th["action"], 0) + 1

#     if summary.get("block", 0) > 0:
#         status = "block"
#     elif summary.get("warn", 0) > 0:
#         status = "warn"

#     return jsonify({"decisions": decisions, "status": status, "summary": summary})

# # Optional: natural-language → policy (stub)
# @app.post("/nl_policy")
# def route_nl_policy():
#     """
#     Body: { "text": "Block merges if more than 5 high-entropy tokens in a single file" }
#     Return: { "rules": [...], "thresholds": [...] }
#     """
#     text = (request.get_json(force=True) or {}).get("text", "")
#     # For now, return a canned translation; later replace with an LLM or template library.
#     return jsonify({
#         "rules": [],
#         "thresholds": [{
#             "id": "too_many_tokens_in_file",
#             "scope": "per_file",
#             "if": 'score > 4.5',
#             "count_gte": 5,
#             "action": "block",
#             "reason": text or "More than 5 high-entropy tokens"
#         }]
#     })

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)
