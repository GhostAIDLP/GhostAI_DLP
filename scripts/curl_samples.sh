# HOW TO RUN (Type these into your terminal):
# 1. chmod +x scripts/curl_samples.sh
# 2. ./scripts/curl_samples.sh

#!/bin/bash
set -euo pipefail

# Use: ./scripts/curl_samples.sh [sync|async]
API="http://127.0.0.1:5000/risk:sync"

send() {
  local label="$1"; shift
  local body="$1"; shift
  echo -e "\n[$label]\n$body"
  curl -s -X POST "$API" -H "Content-Type: application/json" -d "$body" | jq
}

echo "=== LOW (expect LOW severity) ==="

# L1 — benign text
send "L1 benign" \
'{"text":"hello world","tenant_id":"t1","metadata":{"source":"unit-test"}}'

# L2 — harmless code snippet
send "L2 harmless code" \
'{"text":"function add(a,b){ return a+b } // sample","tenant_id":"t1","metadata":{"filename":"utils.js"}}'

# L3 — low-weight keyword (confidential is weight ~0.3)
send "L3 confidential keyword" \
'{"text":"confidential internal use only","tenant_id":"t1","metadata":{"source":"email"}}'


echo -e "\n=== MEDIUM (expect MEDIUM severity) ==="

# M1 — password keyword (keyword_risk: password ~0.55–0.60)
send "M1 password phrase" \
'{"text":"please reset your password immediately","tenant_id":"t1","metadata":{"source":"chat"}}'

# M2 — token keyword (keyword_risk: token ~0.55–0.60)
send "M2 token mention" \
'{"text":"we will rotate the token next sprint","tenant_id":"t1","metadata":{"source":"ticket"}}'

# M3 — base64-ish blob (blob_risk: base64_blob weight ~0.5)
send "M3 base64ish blob" \
'{"text":"Here is a blob: VGhpcyBpcyBhIGJhc2U2NCB0ZXN0IHN0cmluZyB3aXRoIGEgbG9uZ2VyIGxlbmd0aA==","tenant_id":"t1","metadata":{"filename":"blob.txt"}}'

# stuff below here doesn't pass tests
# M4 — DB URI (code_risk medium-tier URI/connection pattern)
send "M4 db uri style" \
'{"text":"postgres://user:pass@db.example.com:5432/appdb","tenant_id":"t1","metadata":{"filename":"config.env"}}'


echo -e "\n=== HIGH (expect HIGH severity) ==="

# H1 — AWS access key (secret_risk: aws, ~0.9)
send "H1 aws key" \
'{"text":"aws_access_key = \"AKIA1234567890EXAMPLE1234\"","tenant_id":"t1","metadata":{"filename":"secrets.py"}}'

# H2 — JWT token (blob_risk or secret_risk: jwt ~0.88)
send "H2 jwt" \
'{"text":"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvZSJ9.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk","tenant_id":"t1","metadata":{"filename":"auth.log"}}'

# H3 — EC private key header (secret_risk: private key ~0.9)
send "H3 pem header" \
'{"text":"-----BEGIN EC PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFA...","tenant_id":"t1","metadata":{"filename":"id_rsa"}}'

# H4 — Slack webhook URL (secret_risk: slack webhook high)
send "H4 slack webhook" \
'{"text":"https://hooks.slack.com/services/T12345678/B876543218/AbCdEfGhIjKlMnOpQrStUvWx24","tenant_id":"t1","metadata":{"filename":"webhook.txt"}}'
