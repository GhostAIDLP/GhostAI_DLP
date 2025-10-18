# GhostAI firewall SDK - Minimal Jinja Demo

## 🎯 Goal
Run one simple command that loads 5 Jinja templates, renders them, sends each to the firewall scanner, and prints detections/blocks.

## ⚙️ Folder Layout
```
ghostai-dlp-sdk/
├── src/ghostai/                  # SDK source
│   ├── __init__.py
│   ├── scanners/
│   └── ...
├── demo_rag/
│   ├── templates/
│   │   ├── safe_prompt.jinja
│   │   ├── leak_payload.jinja
│   │   ├── code_review.jinja
│   │   ├── incident_report.jinja
│   │   └── support_ticket.jinja
│   └── simple_jinja_demo.py     # ⚡️ main demo
├── pyproject.toml
└── README.md
```

## 🚀 How to Run
```bash
# from the repo root
source venv_stable/bin/activate
python demo_rag/simple_jinja_demo.py
```

## 📊 Output
```
🧪 Running GhostAI firewall on 6 Jinja templates...

--- Testing safe_prompt.jinja ---
🚨 BLOCKED: 1 scanner(s) flagged, 1 findings
   📊 presidio: 1 findings

--- Testing leak_payload.jinja ---
🚨 BLOCKED: 2 scanner(s) flagged, 9 findings
   📊 presidio: 4 findings
   📊 regex_secrets: 5 findings

--- Testing code_review.jinja ---
🚨 BLOCKED: 1 scanner(s) flagged, 5 findings
   📊 presidio: 5 findings
```

## 💡 Core Functionality
- **GhostAI SDK** = firewall engine (regex + Presidio + entropy-based detection)
- **Jinja Demo** = shows how runtime rendering can leak data → scanner intercepts it
- **Use Case** = wrap this logic into proxy middleware or RAG pipeline hook

## 🧪 What It Tests
- **safe_prompt.jinja** - Clean template (should pass)
- **leak_payload.jinja** - Malicious template (lots of secrets)
- **code_review.jinja** - Code review workflow
- **incident_report.jinja** - Incident response workflow
- **support_ticket.jinja** - Support ticket workflow
- **api_docs.jinja** - API documentation workflow

All templates are rendered with realistic data and scanned by GhostAI firewall to detect sensitive information leaks.
