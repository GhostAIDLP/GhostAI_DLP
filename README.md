# GhostAI_DLP

# Risk Engine (Day 1 MVP)

## Overview
This service provides synchronous and asynchronous APIs for heuristic risk scoring of text. It detects secrets, SQL injection, and other unsafe patterns using lightweight regex and entropy heuristics.

## Endpoints
- `POST /risk:sync` — returns score inline.
- `POST /risk:async` — accepts payload and (optionally) sends results to `call_back_url`.

Request body:

```json
{
  "text": "string to analyze",
  "tenant_id": "tenant-001",
  "call_back_url": "http://localhost:9000/callback",
  "metadata": { "source": "unit-test" }
}


