# 🚀 Deployment Guide

> **Production deployment, configuration, and operational procedures**

## 🎯 Deployment Overview

### Deployment Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Production Deployment                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Load          │    │   Application   │    │   Data          │        │
│  │   Balancer      │    │   Layer         │    │   Layer         │        │
│  │   (Nginx)       │    │   (K8s Pods)    │    │   (Databases)   │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│           │                       │                       │                │
│           ▼                       ▼                       ▼                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   SSL/TLS       │    │   Firewall      │    │   Redis         │        │
│  │   Termination   │    │   Instances     │    │   Cluster       │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   CDN           │    │   Monitoring    │    │   Backup        │        │
│  │   (CloudFlare)  │    │   Stack         │    │   System        │        │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🐳 Docker Deployment

### Dockerfile Configuration
```dockerfile
# Multi-stage Dockerfile for GhostAI Firewall
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 ghostai && \
    mkdir -p /app && \
    chown -R ghostai:ghostai /app

# Copy application code
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app

# Set working directory
WORKDIR /app

# Switch to non-root user
USER ghostai

# Expose port
EXPOSE 5004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5004/health || exit 1

# Start command
CMD ["python", "run_firewall.py", "--mode=firewall", "--host=0.0.0.0", "--port=5004"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  ghostai-firewall:
    build: .
    ports:
      - "5004:5004"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=sqlite:///data/ghostai_firewall.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - database
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5004/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  database:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ghostai_firewall
      - POSTGRES_USER=ghostai
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ghostai-firewall
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

## ☸️ Kubernetes Deployment

### Kubernetes Manifests
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ghostai-firewall
  labels:
    name: ghostai-firewall

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ghostai-config
  namespace: ghostai-firewall
data:
  LOG_LEVEL: "INFO"
  REDIS_URL: "redis://redis-service:6379"
  DATABASE_URL: "postgresql://ghostai:password@postgres-service:5432/ghostai_firewall"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ghostai-secrets
  namespace: ghostai-firewall
type: Opaque
data:
  database-password: c2VjdXJlX3Bhc3N3b3Jk  # base64 encoded
  redis-password: c2VjdXJlX3JlZGlzX3Bhc3N3b3Jk  # base64 encoded

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ghostai-firewall
  namespace: ghostai-firewall
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ghostai-firewall
  template:
    metadata:
      labels:
        app: ghostai-firewall
    spec:
      containers:
      - name: ghostai-firewall
        image: ghostai/firewall:latest
        ports:
        - containerPort: 5004
        env:
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: ghostai-config
              key: REDIS_URL
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ghostai-secrets
              key: database-password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5004
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5004
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ghostai-firewall-service
  namespace: ghostai-firewall
spec:
  selector:
    app: ghostai-firewall
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5004
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ghostai-firewall-ingress
  namespace: ghostai-firewall
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - firewall.ghostai.com
    secretName: ghostai-tls
  rules:
  - host: firewall.ghostai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ghostai-firewall-service
            port:
              number: 80
```

### Helm Chart
```yaml
# helm/ghostai-firewall/values.yaml
replicaCount: 3

image:
  repository: ghostai/firewall
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
  targetPort: 5004

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: firewall.ghostai.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ghostai-tls
      hosts:
        - firewall.ghostai.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

redis:
  enabled: true
  auth:
    enabled: true
    password: "secure_redis_password"

postgresql:
  enabled: true
  auth:
    postgresPassword: "secure_postgres_password"
    username: "ghostai"
    password: "secure_database_password"
    database: "ghostai_firewall"
```

## 🔧 Configuration Management

### Environment Configuration
```python
# config/settings.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class RedisConfig:
    url: str
    max_connections: int = 100
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

@dataclass
class SecurityConfig:
    secret_key: str
    jwt_secret: str
    encryption_key: str
    rate_limit_per_minute: int = 1000
    max_request_size: int = 1024 * 1024  # 1MB

@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class MonitoringConfig:
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    jaeger_enabled: bool = True
    jaeger_endpoint: Optional[str] = None

class Config:
    def __init__(self):
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'sqlite:///ghostai_firewall.db')
        )
        
        self.redis = RedisConfig(
            url=os.getenv('REDIS_URL', 'redis://localhost:6379')
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv('SECRET_KEY', 'your-secret-key'),
            jwt_secret=os.getenv('JWT_SECRET', 'your-jwt-secret'),
            encryption_key=os.getenv('ENCRYPTION_KEY', 'your-encryption-key')
        )
        
        self.logging = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file_path=os.getenv('LOG_FILE', 'ghostai.log')
        )
        
        self.monitoring = MonitoringConfig(
            prometheus_enabled=os.getenv('PROMETHEUS_ENABLED', 'true').lower() == 'true',
            jaeger_enabled=os.getenv('JAEGER_ENABLED', 'true').lower() == 'true'
        )
```

### Configuration Validation
```python
# config/validator.py
from pydantic import BaseModel, validator
from typing import Optional

class DatabaseConfigValidator(BaseModel):
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    
    @validator('url')
    def validate_database_url(cls, v):
        if not v.startswith(('sqlite://', 'postgresql://', 'mysql://')):
            raise ValueError('Invalid database URL format')
        return v
    
    @validator('pool_size')
    def validate_pool_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Pool size must be between 1 and 100')
        return v

class SecurityConfigValidator(BaseModel):
    secret_key: str
    jwt_secret: str
    encryption_key: str
    rate_limit_per_minute: int = 1000
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters')
        return v
    
    @validator('rate_limit_per_minute')
    def validate_rate_limit(cls, v):
        if v < 1 or v > 10000:
            raise ValueError('Rate limit must be between 1 and 10000')
        return v

def validate_config(config_dict: dict) -> bool:
    """
    Validate configuration dictionary
    """
    try:
        DatabaseConfigValidator(**config_dict.get('database', {}))
        SecurityConfigValidator(**config_dict.get('security', {}))
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy GhostAI Firewall

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t ghostai/firewall:${{ github.sha }} .
        docker build -t ghostai/firewall:latest .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push ghostai/firewall:${{ github.sha }}
        docker push ghostai/firewall:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Kubernetes
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        
        # Update image tag
        sed -i "s|image: ghostai/firewall:.*|image: ghostai/firewall:${{ github.sha }}|g" k8s/deployment.yaml
        
        # Apply manifests
        kubectl apply -f k8s/
        
        # Wait for rollout
        kubectl rollout status deployment/ghostai-firewall -n ghostai-firewall
```

### Deployment Scripts
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Configuration
NAMESPACE="ghostai-firewall"
IMAGE_TAG="${1:-latest}"
ENVIRONMENT="${2:-production}"

echo "Deploying GhostAI Firewall..."
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"
echo "Environment: $ENVIRONMENT"

# 1. Validate configuration
echo "Validating configuration..."
python config/validator.py

# 2. Build and push image
echo "Building Docker image..."
docker build -t ghostai/firewall:$IMAGE_TAG .
docker push ghostai/firewall:$IMAGE_TAG

# 3. Update Kubernetes manifests
echo "Updating Kubernetes manifests..."
sed -i "s|image: ghostai/firewall:.*|image: ghostai/firewall:$IMAGE_TAG|g" k8s/deployment.yaml

# 4. Apply manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 5. Wait for rollout
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/ghostai-firewall -n $NAMESPACE

# 6. Verify deployment
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

echo "Deployment completed successfully!"
```

## 📊 Production Monitoring

### Health Checks
```python
# health_check.py
from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    """
    Comprehensive health check endpoint
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # 1. Database health
    try:
        # Check database connection
        db_status = check_database_health()
        health_status['checks']['database'] = db_status
    except Exception as e:
        health_status['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'unhealthy'
    
    # 2. Redis health
    try:
        redis_status = check_redis_health()
        health_status['checks']['redis'] = redis_status
    except Exception as e:
        health_status['checks']['redis'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'unhealthy'
    
    # 3. Model health
    try:
        model_status = check_model_health()
        health_status['checks']['model'] = model_status
    except Exception as e:
        health_status['checks']['model'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'unhealthy'
    
    # 4. External dependencies
    try:
        external_status = check_external_dependencies()
        health_status['checks']['external'] = external_status
    except Exception as e:
        health_status['checks']['external'] = {'status': 'unhealthy', 'error': str(e)}
    
    return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503

def check_database_health():
    """Check database connectivity and performance"""
    # Implementation for database health check
    return {'status': 'healthy', 'response_time': '5ms'}

def check_redis_health():
    """Check Redis connectivity and performance"""
    # Implementation for Redis health check
    return {'status': 'healthy', 'response_time': '1ms'}

def check_model_health():
    """Check ML model availability and performance"""
    # Implementation for model health check
    return {'status': 'healthy', 'accuracy': '94.2%'}

def check_external_dependencies():
    """Check external service dependencies"""
    # Implementation for external dependency checks
    return {'status': 'healthy', 'dependencies': ['openai', 'anthropic']}
```

### Production Checklist
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Production Deployment Checklist                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Pre-deployment:                                                            │
│  □ Code review completed                                                   │
│  □ Tests passing (unit, integration, e2e)                                 │
│  □ Security scan completed                                                 │
│  □ Performance testing completed                                           │
│  □ Configuration validated                                                 │
│  □ Secrets properly configured                                             │
│  □ Database migrations ready                                               │
│                                                                             │
│  Deployment:                                                                │
│  □ Blue-green deployment configured                                        │
│  □ Load balancer configured                                                │
│  □ SSL/TLS certificates installed                                          │
│  □ Monitoring and alerting configured                                      │
│  □ Logging configured                                                      │
│  □ Backup strategy implemented                                             │
│                                                                             │
│  Post-deployment:                                                           │
│  □ Health checks passing                                                   │
│  □ Performance metrics within thresholds                                   │
│  □ Error rates within acceptable limits                                    │
│  □ Security monitoring active                                              │
│  □ Documentation updated                                                   │
│  □ Team notified of deployment                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Back to**: [Technical README](TECHNICAL_README.md) - Main technical documentation index
