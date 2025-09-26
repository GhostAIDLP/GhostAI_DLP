# --- Config ---
PY        ?= python3
PIP       ?= pip
VENV      ?= .venv
PORT      ?= 5000
APP       ?= app           # flask app import path (e.g., 'app' or 'app:create_app')
FLASK_ENV ?= development

# --- Helper ---
.PHONY: help venv install dev serve cli-install cli up down health fmt test clean

help:
	@echo "Common targets:"
	@echo "  make venv          # create virtual env"
	@echo "  make install       # install deps (app + CLI)"
	@echo "  make dev           # run Flask dev server with reload"
	@echo "  make serve         # run production server (gunicorn)"
	@echo "  make cli-install   # install CLI entrypoint (ghostai-cli)"
	@echo "  make cli ARGS='\"scan this log\"'       # run CLI with prompt"
	@echo "  make cli ARGS='--file auth.log'        # run CLI with file"
	@echo "  make up / make down                    # docker compose up/down"
	@echo "  make health       # curl health endpoint"
	@echo "  make fmt          # format (optional)"
	@echo "  make test         # run tests"
	@echo "  make clean        # remove caches and venv"

venv:
	$(PY) -m venv $(VENV)
	@echo "Run: source $(VENV)/bin/activate"

install: venv
	. $(VENV)/bin/activate && $(PIP) install -U pip
	. $(VENV)/bin/activate && if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi
	. $(VENV)/bin/activate && $(PIP) install -e .

dev:
	. $(VENV)/bin/activate && \
	export FLASK_APP=$(APP) FLASK_ENV=$(FLASK_ENV) && \
	flask run --port $(PORT)

serve:
	. $(VENV)/bin/activate && \
	gunicorn "$(APP):app" --workers 2 --bind 0.0.0.0:$(PORT)

cli-install:
	. $(VENV)/bin/activate && $(PIP) install -e .

# Use: make cli ARGS='"quick scan"'  OR  make cli ARGS='--file auth.log'
cli:
	. $(VENV)/bin/activate && ghostai-cli $(ARGS)

up:
	docker compose up -d

down:
	docker compose down

health:
	curl -fsS http://127.0.0.1:$(PORT)/health || true

fmt:
	. $(VENV)/bin/activate && python -m black . || true
	. $(VENV)/bin/activate && python -m ruff check --fix . || true

test:
	. $(VENV)/bin/activate && pytest -q

clean:
	rm -rf $(VENV) **/__pycache__ .pytest_cache .ruff_cache dist build *.egg-info
