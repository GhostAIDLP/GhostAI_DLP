# ---------- Config (keep in sync with your YAML) ----------
DLP_DIR            ?= dlp_results
GITLEAKS_REPORT    ?= gitleaks.json
TRUFFLEHOG_REPORT  ?= trufflehog.json
TH_EXCLUDE         ?= .trufflehog-exclude.txt
GITLEAKS_CONFIG    ?= .gitleaks.toml
API_APP            ?= api.app:create_app

# Fail policy:
#   FAIL=0 => non-blocking (push/schedule parity)
#   FAIL=1 => fail on findings (PR parity)
FAIL ?= 0
GITLEAKS_EXIT_CODE ?= $(FAIL)

# ---------- Auto-detect binaries; fallback to Docker if missing ----------
GL := $(shell command -v gitleaks 2>/dev/null)
TH := $(shell command -v trufflehog 2>/dev/null)

# Default to local binaries if present; else use Docker images (no local installs needed)
GITLEAKS_BIN      := $(if $(GL),gitleaks,docker run --rm -v "$$PWD:/repo" zricethezav/gitleaks:latest gitleaks)
TRUFFLEHOG_BIN    := $(if $(TH),trufflehog,docker run --rm -v "$$PWD:/repo" ghcr.io/trufflesecurity/trufflehog:latest)

# Paths differ when using Docker: container works in /repo
GITLEAKS_SOURCE        := $(if $(GL),.,/repo)
GITLEAKS_REPORT_PATH   := $(if $(GL),$(GITLEAKS_REPORT),/repo/$(GITLEAKS_REPORT))
GITLEAKS_CONFIG_PATH   := $(if $(GL),$(GITLEAKS_CONFIG),/repo/$(GITLEAKS_CONFIG))

TRUFFLEHOG_FS_PATH     := $(if $(TH),.,/repo)
TRUFFLEHOG_EXCLUDE_PATH:= $(if $(TH),$(TH_EXCLUDE),/repo/$(TH_EXCLUDE))

.PHONY: help clean api-up dlp gitleaks trufflehog trufflehog-exclude normalize scan scan-pr

help:
	@echo "make scan       # clean, API up, DLP, gitleaks, trufflehog, normalize (non-blocking)"
	@echo "make scan-pr    # same as scan, but fail on findings (PR parity)"
	@echo "make clean      # remove generated artifacts"
	@echo "make gitleaks   # run only gitleaks (to $(GITLEAKS_REPORT))"
	@echo "make trufflehog # run only trufflehog (to $(TRUFFLEHOG_REPORT))"

clean:
	rm -rf $(DLP_DIR) $(GITLEAKS_REPORT) $(TRUFFLEHOG_REPORT) /tmp/flask.log $(TH_EXCLUDE)
	mkdir -p $(DLP_DIR)

api-up:
	nohup uv run flask --app $(API_APP) run --host 127.0.0.1 --port=5000 > /tmp/flask.log 2>&1 & \
	sleep 2 && curl -sf http://127.0.0.1:5000/health

dlp:
	find . -type d \( -name .git -o -name .venv -o -name venv -o -name node_modules -o -name $(DLP_DIR) \) -prune -o \
	       -type f -name "*.py" -print0 | \
	xargs -0 -I {} sh -c 'echo "🔍 Scanning {}"; uv run python -m src.cli.auto_cli < "{}" > "$(DLP_DIR)/$$(basename {}).json" || true'

# ---------- Gitleaks ----------
gitleaks:
	@echo ">> Using Gitleaks: $(if $(GL),local binary,$(GITLEAKS_BIN))"
	@CFG=""; if [ -f "$(GITLEAKS_CONFIG)" ]; then CFG="--config $(GITLEAKS_CONFIG_PATH)"; echo ">> Config: $(GITLEAKS_CONFIG)"; fi; \
	$(GITLEAKS_BIN) detect --no-git --source $(GITLEAKS_SOURCE) $$CFG \
	  --report-format json --report-path "$(GITLEAKS_REPORT_PATH)" --exit-code $(GITLEAKS_EXIT_CODE)
	test -s "$(GITLEAKS_REPORT)"    # ensure host file exists even with Docker
	head -n 3 "$(GITLEAKS_REPORT)" || true

# ---------- TruffleHog ----------
trufflehog-exclude:
	@printf '%s\n' \
	'^\.git/' '^node_modules/' '^\.venv/' '^venv/' \
	'^alembic/' '^$(DLP_DIR)/' \
	'^datasets/secret_risk\.yaml$$' > "$(TH_EXCLUDE)"

# NOTE the dependency on trufflehog-exclude
trufflehog: trufflehog-exclude
	@echo ">> Using TruffleHog: $(if $(TH),local binary,$(TRUFFLEHOG_BIN))"
	# ensure exclude exists even if someone runs this target directly
	@[ -f "$(TH_EXCLUDE)" ] || (echo "creating $(TH_EXCLUDE)"; \
	  printf '%s\n' '^\.git/' '^node_modules/' '^\.venv/' '^venv/' '^alembic/' '^$(DLP_DIR)/' '^datasets/secret_risk\.yaml$$' > "$(TH_EXCLUDE)")
	@if [ "$(FAIL)" = "1" ]; then \
	  set -e; \
	  $(TRUFFLEHOG_BIN) filesystem $(TRUFFLEHOG_FS_PATH) \
	    --results=verified,unknown \
	    --no-update \
	    --json \
	    --exclude-paths "$(TRUFFLEHOG_EXCLUDE_PATH)" \
	    --fail \
	    > "$(TRUFFLEHOG_REPORT)"; \
	else \
	  $(TRUFFLEHOG_BIN) filesystem $(TRUFFLEHOG_FS_PATH) \
	    --results=verified,unknown \
	    --no-update \
	    --json \
	    --exclude-paths "$(TRUFFLEHOG_EXCLUDE_PATH)" \
	    > "$(TRUFFLEHOG_REPORT)" || true; \
	fi
	test -f "$(TRUFFLEHOG_REPORT)"
	head -n 3 "$(TRUFFLEHOG_REPORT)" || true



# ---------- Normalize ----------
normalize:
	uv run python src/normalize_reports.py \
	  --gitleaks   "$(GITLEAKS_REPORT)" \
	  --trufflehog "$(TRUFFLEHOG_REPORT)" \
	  --out "$(DLP_DIR)"
	@echo "normalized files:" $$(find "$(DLP_DIR)" -name "*.json" | wc -l)

# Default: non-blocking (push/schedule behavior)
scan: clean api-up dlp gitleaks trufflehog normalize

# PR parity: fail on findings
scan-pr: GITLEAKS_EXIT_CODE=1
scan-pr: FAIL=1
scan-pr: scan