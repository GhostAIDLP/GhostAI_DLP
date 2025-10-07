from flask import Flask, request, jsonify
import requests, os

from ghostai.pipeline.pipeline import Pipeline

app = Flask(__name__)

# Point this at OpenAI or Anthropic
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔧 Init pipeline with rules-as-code config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scanners.yaml")
pipeline = Pipeline(config_path=CONFIG_PATH)

@app.route("/v1/chat/completions", methods=["POST"])
def proxy_chat():
    body = request.get_json()

    if "messages" in body:
        for msg in body["messages"]:
            if msg.get("role") == "user":
                text = msg["content"]

                # 🚦 Run pipeline on user input
                res = pipeline.run(text)

                # 🔁 Look for any scanner-provided replacement text
                for b in res["breakdown"]:
                    extra = b.get("extra", {})
                    if "anonymized" in extra:
                        text = extra["anonymized"]
                    elif "redacted" in extra:
                        text = extra["redacted"]

                # 🪵 Log flags for observability
                if res["flags"]:
                    app.logger.warning(
                        f"[PIPELINE] Flags={res['flags']} | "
                        f"Score={res['score']} | Breakdown={res['breakdown']}"
                    )

                # Replace message content with possibly modified text
                msg["content"] = text

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    resp = requests.post(
        f"{OPENAI_API_BASE}/chat/completions",
        headers=headers,
        json=body,
        timeout=30
    )
    return jsonify(resp.json()), resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
