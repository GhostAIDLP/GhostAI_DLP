# GhostAI DLP SDK Makefile

.PHONY: setup run proxy test clean help

# Default target
help:
	@echo "GhostAI DLP SDK - Available targets:"
	@echo "  setup    - Create virtual environment and install dependencies"
	@echo "  run      - Run CLI with example text"
	@echo "  proxy    - Start the proxy server"
	@echo "  test     - Run all tests"
	@echo "  clean    - Clean up virtual environment"
	@echo "  help     - Show this help message"

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up GhostAI DLP SDK..."
	python3.12 -m venv venv
	@echo "Activating virtual environment and installing dependencies..."
	. venv/bin/activate && pip install -U pip wheel setuptools
	. venv/bin/activate && pip install -e .
	@echo "Setup complete! Activate with: source venv/bin/activate"

# Run CLI with example text
run:
	@echo "Running GhostAI CLI with example text..."
	. venv/bin/activate && python -m ghostai "My SSN is 123-45-6789 and my email is test@example.com"

# Start the proxy server
proxy:
	@echo "Starting GhostAI proxy server on port 5000..."
	@echo "Note: Set OPENAI_API_KEY environment variable for full functionality"
	. venv/bin/activate && python -m ghostai.proxy_api.proxy

# Run tests
test:
	@echo "Running tests..."
	. venv/bin/activate && python -m pytest tests/ -v

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf src/ghostai/__pycache__/
	rm -rf src/ghostai/*/__pycache__/
	rm -rf .pytest_cache/