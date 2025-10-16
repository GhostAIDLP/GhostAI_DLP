# GhostAI DLP SDK

Data Loss Prevention pipeline with multiple scanners (PII, secrets, prompt injection), a CLI/proxy, and optional real-time logging + dashboard.

## Features
- Presidio-based PII detection
- Regex-based secrets and jailbreak heuristics
- Optional external scanners: TruffleHog, GitLeaks
- Optional PromptGuard2 (HuggingFace Inference) for injection detection
- Latency measurement and structured breakdown
- Default SQLite logging; optional Postgres/Redis/Streamlit stack

## Requirements
- Python 3.12
- pip-installed deps from `requirements.txt`
- Optional:
  - `trufflehog` and `gitleaks` binaries on PATH
  - `HF_TOKEN` for PromptGuard2 (paid credits may be required)

## Install
```bash
python -m venv ghostai_env
source ghostai_env/bin/activate
pip install -r requirements.txt
```

## Configuration
Scanners are configured in `src/ghostai/config/scanners.yaml`. Current runtime defaults:

```yaml
profiles:
  runtime:
    presidio:
      enabled: true
      anonymize: true
    trufflehog:
      enabled: true           # requires trufflehog binary
    gitleaks:
      enabled: true           # requires gitleaks binary
    promptguard2:
      enabled: true           # requires HF_TOKEN/credits
      threshold: 0.85
    regex_secrets:
      enabled: true
```

If external binaries or HF credits are missing, those scanners return non-fatal errors in the breakdown; others still run.

## Quick Test
```bash
python -c "from src.ghostai.pipeline.pipeline import Pipeline; p=Pipeline(); print(p.run('My SSN is 123-45-6789'))"
```

Expected: `regex_secrets` should flag SSN; Presidio may flag depending on local models; external scanners may error if not installed.

## External Tools (optional)
Install on macOS with Homebrew:
```bash
brew install trufflehog gitleaks
```

## Logging
- Default: SQLite via `ghostai.database_logger_sqlite`
- Optional advanced stack (Postgres/Redis/Streamlit): see `REALTIME_LOGGING.md`

## Docker
See `README-Docker.md` for container builds and deployment.

## License
See `LICENSE`.
