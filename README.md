# GhostAI DLP SDK 🕵️‍♂️🔐

A unified Data Loss Prevention (DLP) and GenAI Security Scanning Pipeline for Apple Silicon (arm64).

## Quick Start (Apple Silicon)

### 1. Prerequisites

- Python 3.12+ (recommended for Apple Silicon)
- macOS with Apple Silicon (M1/M2/M3)

### 2. Setup

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install -U pip wheel setuptools
pip install -e .

# Or use the Makefile
make setup
```

### 3. CLI Usage

```bash
# Scan text directly
python -m ghostai "My SSN is 123-45-6789"

# Interactive mode
python -m ghostai
```

### 4. Proxy Server

```bash
# Start the proxy server (requires OPENAI_API_KEY)
export OPENAI_API_KEY=your_key_here
python -m ghostai.proxy_api.proxy

# Or use the Makefile
make proxy
```

### 5. Test the Proxy

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"my aws key is AKIA123..."}]}'
```

## Features

- **CLI Interface**: Direct text scanning with `python -m ghostai`
- **Proxy Server**: OpenAI-compatible API with DLP scanning
- **Multiple Scanners**: Presidio (PII), PromptGuard2 (injection), TruffleHog, GitLeaks
- **Apple Silicon Optimized**: All dependencies tested on arm64
- **Editable Install**: Development-friendly with `pip install -e .`

## API Reference

### Pipeline

```python
from ghostai import Pipeline

pipeline = Pipeline()
result = pipeline.run("My SSN is 123-45-6789")
print(result)
# {
#   "score": 1.0,
#   "flags": ["presidio"],
#   "breakdown": [...]
# }
```

### GhostAIProxy

```python
from ghostai import GhostAIProxy

proxy = GhostAIProxy()
proxy.run(port=5000)
```

## Testing

```bash
# Run all tests
make test

# Or directly
python -m pytest tests/ -v
```

## Troubleshooting

**Import Error**: Make sure you're in the project root and have activated the virtual environment.

**Port 5000 in use**: macOS AirPlay uses port 5000. Use a different port:
```bash
python -c "from ghostai.proxy_api.proxy import GhostAIProxy; GhostAIProxy().run(port=5001)"
```

**Missing dependencies**: Ensure you're using Python 3.12+ and have installed with `pip install -e .`

---

## New Direction: Automation Mode

We now support an automation-friendly CLI (`src/cli/auto_cli.py`).
Unlike the interactive mode, this:

* Reads input piped from stdin or from CLI args
* Outputs raw JSON
* Is designed for GitHub Actions / CI integration

Example:

```bash
echo "print('hello')" | python3 -m src.cli.automate
```

---

## New Direction: GitHub Actions Integration

## GitHub Actions Integration (DLP)

A workflow at `.github/workflows/dlp.yml` now:

- Runs on every push/PR to `main` (and can be triggered manually).
- Sets up Python (via `uv`) and starts the Flask API.
- Scans repository files with our internal DLP (`src.cli.auto_cli`).
- Runs **Gitleaks** and **TruffleHog (filesystem)**.
- Normalizes results into `dlp_results/` and uploads artifacts.

**Run it locally (parity with CI):**
```bash
make scan      # non-blocking
make scan-pr   # PR-style: fails on verified findings
# Tip: start fresh if needed
make clean && make scan
```

---

## New Direction: Automated Ingestion into Database

We now support exporting scan results into a Postgres database.

- **Artifacts:** All detectors write per-file JSONs into `dlp_results/`.
- **Uploader:** Run `python src/upload_results.py --repo <org/repo>` to insert results into Postgres.
- **Schema:** Rows include file path, detector, severity, score, reasons, and timestamps.

Example verification:

```sql
SELECT detector, COUNT(*) FROM dlp_findings GROUP BY 1;
```

---

## New Direction: Repo File Scanning

Instead of static test snippets, the plan is to:

* Recursively scan `.py` (or all) files in the repo
* Collect JSON results into `dlp_results.json`
* Upload as a GitHub Actions artifact

This will let us build a dataset of findings automatically.

---

## New Direction: AI Post-Filtering

We’ll eventually add a RAG + embeddings layer to filter down false positives (FPs).

* Baseline FP goal: <10% for common secret detectors.
* Long-term: AI filter to re-rank findings before surfacing.


