from flask import Flask, request, jsonify
import requests, os, torch
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = Flask(__name__)

# Point this at OpenAI or Anthropic
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔍 Init Presidio
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# 🔍 Init PromptGuard 2
MODEL_NAME = "meta-llama/PromptGuard-2"   # ⚡ replace with actual HF repo
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def redact_text(text: str) -> str:
    """Run Presidio detection + anonymization on input text."""
    results = analyzer.analyze(text=text, language="en")
    if results:
        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized.text
    return text

def check_promptguard(prompt: str, threshold: float = 0.8) -> tuple[bool, float]:
    """Run PromptGuard check on input text."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1).squeeze()
        malicious_score = scores[1].item()  # assume index 1 = malicious
        return malicious_score >= threshold, malicious_score
@app.route("/v1/chat/completions", methods=["POST"])
def proxy_chat():
    body = request.get_json()

    if "messages" in body:
        for msg in body["messages"]:
            if msg.get("role") == "user":
                # Step 1: Presidio redaction
                text = redact_text(msg["content"])

                # Step 2: PromptGuard (log only)
                flagged, score = check_promptguard(text)
                if flagged:
                    # ⚠️ Just log locally for now
                    app.logger.warning(f"[PromptGuard] Flagged injection (score={score:.2f}): {text}")

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
