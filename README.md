# GhostAI_DLP 🕵️‍♂️🔐

A developer-first Data Loss Prevention (DLP) tool for detecting risky patterns in code.
Built with Flask + Python CLI.

---

## Roadmap

* [x] CLI-based detection engine (secrets, blobs, entropy)
* [ ] Pre-commit + GitHub CI integration
* [ ] AI post-processing filter to reduce false positives
* [ ] SaaS dashboard for org-wide reporting

---

## CLI Usage (Important!)

The CLI lives under `src/cli/`.
Because this project uses packages (`src/`), you must run the CLI with Python’s module flag (`-m`) from the project root.

### Interactive Mode

Run:

```bash
python3 -m src.cli.cli
```

Example session:

```bash
Enter a code prompt (or type 'exit' to quit): // detector test: obvious AWS creds (FAKE ONLY)
Enter the next line (or press Enter to submit): const AWS = require('aws-sdk');
...

{
    "score": 0.98,
    "severity": "high",
    "breakdown": [
        { "name": "secrets", "score": 0.9, "reasons": ["aws_access_key detected"] },
        { "name": "keywords", "score": 0.6, "reasons": ["keyword_secret detected"] }
    ]
}
```

The CLI sends the snippet to the Flask API and prints a JSON result with:

* score
* severity
* breakdown of detectors triggered

---

## Setup & Running Flask

### 1. Prerequisites

Make sure you have Python 3.x installed:

```bash
python3 --version
```

If you don’t have Python installed, download it from [python.org/downloads](https://www.python.org/downloads).

Also ensure pip (Python’s package manager) is installed:

```bash
pip --version
```

### 2. Install Virtual Environment

```bash
pip install virtualenv
```

### 3. Create a Virtual Environment

```bash
python3 -m venv .venv
```

This will create a folder named `.venv/` that contains your isolated environment.

### 4. Activate the Virtual Environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows (PowerShell)**

```bash
.venv\Scripts\activate
```

When activated, you’ll see `(.venv)` in your terminal prompt.
To deactivate at any time:

```bash
deactivate
```

### 5. Install Dependencies

With the environment activated:

```bash
pip install -r requirements.txt
```

### 6. Run the Flask API

From the project root:

```bash
flask --app src/api/routers/risk run
```

Flask will run at:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

### 7. Deactivate the Virtual Environment

When finished:

```bash
deactivate
```

---

## Troubleshooting

**Error:** `ModuleNotFoundError: No module named 'src'`
**Fix:** Always run with `-m`:

```bash
python3 -m src.cli.cli
```

**Warning:** `NotOpenSSLWarning from urllib3`
This is non-blocking — safe to ignore in development.

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


