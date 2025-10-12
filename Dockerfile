# Multi-stage Dockerfile for GhostAI DLP SDK
# Supports both ARM64 (Apple Silicon) and x86_64 (Intel/AMD)

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install external tools (TruffleHog & GitLeaks)
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        TRUFFLEHOG_ARCH="amd64"; \
        GITLEAKS_ARCH="x64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        TRUFFLEHOG_ARCH="arm64"; \
        GITLEAKS_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    # Install TruffleHog
    curl -L "https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_3.63.0_linux_${TRUFFLEHOG_ARCH}.tar.gz" | \
    tar -xz -C /usr/local/bin/ && \
    # Install GitLeaks
    curl -L "https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_8.18.0_linux_${GITLEAKS_ARCH}.tar.gz" | \
    tar -xz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/trufflehog /usr/local/bin/gitleaks

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip wheel setuptools && \
    pip install -e .

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash ghostai && \
    chown -R ghostai:ghostai /app
USER ghostai

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import ghostai; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "ghostai.proxy_api.proxy"]
