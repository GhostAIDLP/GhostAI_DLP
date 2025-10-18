# 🐳 GhostAI firewall SDK - Docker Deployment Guide

> **Cross-platform containerized deployment for GhostAI firewall SDK**

## 🚀 Quick Start

### Prerequisites
- **Docker** 20.10+ with BuildKit support
- **Docker Compose** 2.0+
- **8GB RAM** minimum (16GB recommended)

### 🏗️ Build & Run

#### Option 1: Docker Compose (Recommended)
```bash
# Clone and navigate
git clone https://github.com/your-org/ghostai-dlp-sdk.git
cd ghostai-dlp-sdk

# Set environment variables
export OPENAI_API_KEY="your_openai_key_here"
export HF_TOKEN="your_huggingface_token_here"  # Optional

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ghostai-dlp
```

#### Option 2: Manual Docker Build
```bash
# Build for your platform
./scripts/docker-build.sh

# Run the container
docker run -p 5000:5000 \
  -e OPENAI_API_KEY="your_key_here" \
  ghostai-dlp:latest
```

#### Option 3: Multi-Platform Build
```bash
# Build for both ARM64 and x86_64
./scripts/docker-build.sh --platform both --push

# This creates images for:
# - linux/amd64 (Intel/AMD)
# - linux/arm64 (Apple Silicon, ARM servers)
```

## 🌍 Cross-Platform Support

| Platform | Status | Docker Image | Notes |
|----------|--------|--------------|-------|
| **Linux x86_64** | ✅ **Supported** | `linux/amd64` | Intel/AMD servers |
| **Linux ARM64** | ✅ **Supported** | `linux/arm64` | ARM servers, Apple Silicon |
| **macOS Apple Silicon** | ✅ **Supported** | `linux/arm64` | Via Docker Desktop |
| **macOS Intel** | ✅ **Supported** | `linux/amd64` | Via Docker Desktop |
| **Windows** | ✅ **Supported** | `linux/amd64` | Via Docker Desktop/WSL2 |

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-proj-...          # Your OpenAI API key

# Optional
HF_TOKEN=hf_...                     # HuggingFace token for PromptGuard2
POSTGRES_USER=ghostai               # Database user
POSTGRES_PASSWORD=ghostai123        # Database password
POSTGRES_DB=ghostai                 # Database name
POSTGRES_PORT=5432                  # Database port
```

### Scanner Configuration
The SDK uses `src/ghostai/config/scanners.yaml` to configure which scanners are enabled. Current defaults in code:

```yaml
profiles:
  runtime:
    presidio:
      enabled: true
      anonymize: true
    regex_secrets:
      enabled: true
    trufflehog:
      enabled: true   # Requires external binary in container or host
    gitleaks:
      enabled: true   # Requires external binary in container or host
    promptguard2:
      enabled: true   # Requires HF_TOKEN and sufficient credits
      threshold: 0.85
```

Notes:
- If `trufflehog`/`gitleaks` aren't available in the image/host PATH, those scanners will return non-fatal errors in the breakdown.
- If `HF_TOKEN` is unset or quota is exceeded, PromptGuard2 returns a non-fatal error in the breakdown.

## 🧪 Testing the Deployment

### 1. Health Check
```bash
# Check if the service is running
curl http://localhost:5000/health

# Or check Docker logs
docker-compose logs ghostai-dlp
```

### 2. CLI Testing
```bash
# Test the CLI inside the container
docker-compose exec ghostai-dlp python -m ghostai "My SSN is 123-45-6789"

# Expected: regex_secrets will flag; Presidio may flag; external scanners may error if binaries missing; PromptGuard2 needs HF_TOKEN/credits
```

### 3. API Testing
```bash
# Test the proxy API
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "My API key is sk-1234567890abcdef"}
    ]
  }'

# Expected: Returns anonymized response with sensitive data replaced
```

## 🏭 Production Deployment

### Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml ghostai-dlp

# Scale services
docker service scale ghostai-dlp_ghostai-dlp=3
```

### Kubernetes
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ghostai-dlp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ghostai-dlp
  template:
    metadata:
      labels:
        app: ghostai-dlp
    spec:
      containers:
      - name: ghostai-dlp
        image: ghostai-dlp:latest
        ports:
        - containerPort: 5000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "trufflehog: command not found"
```bash
# Check if external tools are installed
docker-compose exec ghostai-dlp which trufflehog
docker-compose exec ghostai-dlp which gitleaks

# If missing, rebuild the image
docker-compose build --no-cache ghostai-dlp
```

#### 2. "ModuleNotFoundError: No module named 'presidio'"
```bash
# Check Python dependencies
docker-compose exec ghostai-dlp pip list | grep presidio

# Rebuild if missing
docker-compose build --no-cache ghostai-dlp
```

#### 3. "Connection refused" on API calls
```bash
# Check if service is running
docker-compose ps

# Check logs for errors
docker-compose logs ghostai-dlp

# Restart if needed
docker-compose restart ghostai-dlp
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats

# Scale up if needed
docker-compose up -d --scale ghostai-dlp=2
```

### Debug Mode
```bash
# Run in debug mode
docker-compose -f docker-compose.yml -f docker-compose.override.yml up ghostai-dev

# Or run with debug logging
docker run -p 5000:5000 \
  -e FLASK_DEBUG=1 \
  -e FLASK_ENV=development \
  ghostai-dlp:latest
```

## 📊 Monitoring & Observability

### Health Checks
```bash
# Built-in health check
docker inspect --format='{{.State.Health.Status}}' ghostai-dlp_ghostai-dlp_1

# Custom health check
curl -f http://localhost:5000/health || exit 1
```

### Logging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ghostai-dlp

# Follow logs in real-time
docker-compose logs --tail=100 -f ghostai-dlp
```

### Metrics (Future)
- Prometheus metrics endpoint (planned)
- Grafana dashboards (planned)
- Custom firewall metrics (planned)

## 🚀 Advanced Usage

### Custom Scanner Configuration
```bash
# Mount custom config
docker run -p 5000:5000 \
  -v ./custom-scanners.yaml:/app/src/ghostai/config/scanners.yaml \
  -e OPENAI_API_KEY="your_key" \
  ghostai-dlp:latest
```

### Development Mode
```bash
# Run with hot reload
docker-compose --profile dev up ghostai-dev

# Or manually
docker run -p 5001:5000 \
  -v ./src:/app/src \
  -v ./demo_rag:/app/demo_rag \
  -e FLASK_DEBUG=1 \
  ghostai-dlp:latest
```

### Multi-Architecture Build
```bash
# Build and push for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghostai-dlp:latest \
  --push .
```

## 📋 Summary

✅ **Cross-platform support** - Works on Linux, macOS, Windows  
✅ **Multi-architecture** - ARM64 and x86_64 support  
✅ **Production ready** - Health checks, logging, monitoring  
✅ **Easy deployment** - Docker Compose, Kubernetes, Docker Swarm  
✅ **Development friendly** - Hot reload, debug mode  
✅ **External tool support** - TruffleHog, GitLeaks included  

The GhostAI firewall SDK is now fully containerized and ready for deployment across any environment! 🎉
