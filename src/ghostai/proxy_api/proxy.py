# src/ghostai/proxy_api/proxy.py

from flask import Flask, request, jsonify
import requests, os, logging
from ghostai.pipeline.pipeline import Pipeline


class GhostAIProxy:
    def __init__(self, api_base=None, api_key=None, config_path=None, use_mock=False):
        self.app = Flask(__name__)
        self.use_mock = use_mock
        if use_mock:
            self.api_base = api_base or "http://localhost:5005"
            self.api_key = "mock-key"
        else:
            self.api_base = api_base or "https://api.openai.com/v1"
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # resolve config file path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = config_path or os.path.join(base_dir, "config", "scanners.yaml")

        self.pipeline = Pipeline(config_path=config_path)
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/v1/chat/completions", methods=["POST"])
        def proxy_chat():
            try:
                body = request.get_json()
                if not body:
                    return jsonify({"error": "No JSON body provided"}), 400
                
                # Extract session information for logging
                session_id = request.headers.get('X-Session-ID', 'proxy-session')
                user_agent = request.headers.get('User-Agent', 'unknown')
                ip_address = request.remote_addr

                # 🔍 run firewall scans
                if "messages" in body:
                    for msg in body["messages"]:
                        if msg.get("role") == "user":
                            text = msg["content"]
                            res = self.pipeline.run(
                                text, 
                                session_id=session_id,
                                user_agent=user_agent,
                                ip_address=ip_address
                            )

                            # modify text if redacted/anonymized
                            for b in res["breakdown"]:
                                extra = b.get("extra", {})
                                if "anonymized" in extra:
                                    text = extra["anonymized"]
                                elif "redacted" in extra:
                                    text = extra["redacted"]

                            if res["flags"]:
                                logging.warning(
                                    f"[PIPELINE] Flags={res['flags']} | Score={res['score']} | Breakdown={res['breakdown']}"
                                )

                            msg["content"] = text

                # 🚀 forward to LLM (OpenAI or Mock)
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                if self.use_mock:
                    # For mock, don't send auth header
                    headers = {"Content-Type": "application/json"}
                
                resp = requests.post(
                    f"{self.api_base}/v1/chat/completions",
                    headers=headers,
                    json=body,
                    timeout=30,
                )
                return jsonify(resp.json()), resp.status_code
                
            except Exception as e:
                logging.error(f"Proxy error: {str(e)}")
                return jsonify({"error": f"Proxy error: {str(e)}"}), 500

    def run(self, host="0.0.0.0", port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    GhostAIProxy().run()
