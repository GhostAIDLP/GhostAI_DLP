# 🔍 Real-time Logging & Analytics System

> Default logging uses SQLite. PostgreSQL, Redis, and the Streamlit dashboard are optional components you can enable for advanced, real-time analytics.

## 📋 Overview

The GhostAI firewall SDK now includes a comprehensive real-time logging and analytics system that captures, stores, and visualizes all firewall scan results. This system provides enterprise-grade observability, security, and performance monitoring.

## 🏗️ Architecture

```mermaid
graph TB
    A[GhostAI Pipeline/CLI/Proxy] --> B[Database Logger]
    B --> C[PostgreSQL Database]
    B --> D[Redis Cache]
    C --> E[Streamlit Dashboard]
    D --> E
    F[Data Retention Script] --> C
    G[Encryption Layer] --> C
```

## 🗄️ Database Schema

### Enhanced `dlp_findings` Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `session_id` | VARCHAR(255) | Session identifier for tracking |
| `input_hash` | VARCHAR(64) | SHA256 hash of input text (privacy) |
| `score` | FLOAT | Risk score (0.0-1.0) |
| `flags` | JSONB | List of triggered scanner flags |
| `reasons` | JSONB | Detailed breakdown (unencrypted) |
| `encrypted_reasons` | TEXT | Encrypted breakdown data |
| `is_encrypted` | BOOLEAN | Flag for encrypted data |
| `severity` | TEXT | Risk severity (Critical/High/Medium/Low/Info) |
| `latency_ms` | FLOAT | Scan latency in milliseconds |
| `environment` | VARCHAR(50) | Environment (docker/local/kubernetes/etc.) |
| `user_agent` | TEXT | Client user agent |
| `ip_address` | VARCHAR(45) | Client IP address |
| `created_at` | TIMESTAMP | Record creation time |

### Legacy Fields (for batch uploads)
- `repo`, `file_path`, `detector`, `line_count`, `avg_line_len`, `max_line_len`

## 🚀 Quick Start

### 1. Default (SQLite only)

This works out of the box. No extra services required. The pipeline logs to a local SQLite DB via `ghostai.database_logger_sqlite`.

### 2. Start the Optional Full Stack (Postgres/Redis/Streamlit)

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Access the Optional Dashboard

- **Dashboard**: http://localhost:8501
- **Database Admin**: http://localhost:8080
- **API Proxy**: http://localhost:5000

### Test Logging

```bash
# Test CLI with logging
docker run -it ghostai-dlp python -m ghostai "My SSN is 123-45-6789"

# Test API with session tracking
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: test-session-123" \
  -d '{"messages":[{"role":"user","content":"AWS key: AKIAIOSFODNN7EXAMPLE"}]}'
```

## 📊 Features

### 🔍 Real-time Logging
- **Automatic Logging**: All `Pipeline.run()` calls are logged (SQLite by default; Postgres when enabled)
- **Session Tracking**: Track user sessions across multiple scans
- **Performance Metrics**: Latency and throughput monitoring
- **Environment Detection**: Automatic detection of Docker/K8s/Cloud environments

### 🔐 Security & Privacy
- **Input Hashing**: SHA256 hashing of input text for privacy
- **Encryption**: Optional encryption of sensitive breakdown data
- **Data Retention**: Automatic cleanup of old records (30 days default)
- **Access Control**: Database-level access controls

### 📈 Analytics & Monitoring
- **Real-time Dashboard**: Streamlit-based analytics dashboard
- **Performance Metrics**: Latency, throughput, and error rates
- **Risk Analysis**: Score distribution and severity breakdown
- **Environment Analytics**: Performance by environment type

### ⚡ Caching & Performance
- **Redis Caching**: Frequent query caching for improved performance
- **Connection Pooling**: Efficient database connection management
- **Async Logging**: Non-blocking database writes

## 🛠️ Configuration

### Environment Variables

```bash
# Default: SQLite (no env needed)

# Optional: Postgres/Redis
DATABASE_URL=postgresql://ghostai:ghostai123@db:5432/ghostai
POSTGRES_USER=ghostai
POSTGRES_PASSWORD=ghostai123
POSTGRES_DB=ghostai
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Encryption (Optional)
ENCRYPTION_KEY=your-base64-encoded-key
```

### Pipeline Configuration

```python
from ghostai import Pipeline

# Enable logging (default: True)
pipeline = Pipeline(enable_logging=True)

# Disable logging for performance-critical scenarios
pipeline = Pipeline(enable_logging=False)

# Run with session tracking
result = pipeline.run(
    text="sensitive data here",
    session_id="user-session-123",
    user_agent="my-app/1.0",
    ip_address="192.168.1.100"
)
```

## 📊 Dashboard Features

### Main Metrics
- **Total Scans**: Number of scans in selected time range
- **High Risk Scans**: Scans with score ≥ 0.7
- **Average Latency**: Mean scan latency
- **Active Sessions**: Unique session count

### Visualizations
- **Risk Score Distribution**: Histogram of scan scores
- **Severity Breakdown**: Pie chart of risk levels
- **Time Series**: Scan activity over time
- **Environment Analysis**: Performance by environment

### Data Tables
- **Recent Scans**: Latest scan results with filtering
- **Session Tracking**: Scans grouped by session
- **Performance Metrics**: Latency and throughput data

## 🔧 Management & Maintenance

### Data Retention

```bash
# View database statistics
python scripts/cleanup_old_data.py --stats

# Dry run cleanup (show what would be deleted)
python scripts/cleanup_old_data.py --days 30 --dry-run

# Clean up records older than 30 days
python scripts/cleanup_old_data.py --days 30

# Clean up records older than 7 days
python scripts/cleanup_old_data.py --days 7
```

### Database Migrations

```bash
# Apply new migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback migration
alembic downgrade -1
```

### Monitoring & Health Checks

```bash
# Test real-time logging
python scripts/test_realtime_logging.py

# Check service health
docker-compose ps
curl http://localhost:8501/_stcore/health  # Dashboard
curl http://localhost:5000/health          # API
```

## 🔒 Security Considerations

### Data Protection
- **Input Hashing**: All input text is hashed before storage
- **Encryption**: Sensitive breakdown data can be encrypted
- **Access Control**: Database access is restricted to application containers
- **Network Security**: Services communicate over internal Docker networks

### Compliance
- **Data Retention**: Automatic cleanup prevents indefinite data storage
- **Audit Trail**: Complete audit trail of all scan activities
- **Privacy**: No raw input text stored, only hashes
- **Encryption**: Optional encryption for sensitive data

## 📈 Performance Optimization

### Database Optimization
- **Indexes**: Optimized indexes on frequently queried fields
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized queries for dashboard analytics

### Caching Strategy
- **Redis Caching**: Frequent queries cached for 30 minutes
- **Session Caching**: Recent scans cached for 1 hour
- **Query Caching**: Dashboard queries cached for improved performance

### Monitoring
- **Latency Tracking**: All scans include latency measurements
- **Error Tracking**: Failed scans are logged with error details
- **Resource Usage**: Memory and CPU usage monitoring

## 🚨 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database status
docker-compose logs db

# Verify connection
docker exec -it ghostai-dlp-db-1 psql -U ghostai -d ghostai -c "SELECT 1;"
```

**Redis Connection Failed**
```bash
# Check Redis status
docker-compose logs redis

# Test Redis connection
docker exec -it ghostai-dlp-redis-1 redis-cli ping
```

**Dashboard Not Loading**
```bash
# Check dashboard logs
docker-compose logs dashboard

# Verify database connectivity from dashboard
docker exec -it ghostai-dlp-dashboard-1 python -c "from sqlalchemy import create_engine; print(create_engine('postgresql://ghostai:ghostai123@db:5432/ghostai').connect())"
```

**High Memory Usage**
```bash
# Check memory usage
docker stats

# Clean up old data
python scripts/cleanup_old_data.py --days 7
```

### Performance Tuning

**Database Performance**
- Increase `shared_buffers` in PostgreSQL
- Add more indexes for frequently queried fields
- Consider read replicas for dashboard queries

**Redis Performance**
- Increase Redis memory limit
- Use Redis clustering for high availability
- Implement Redis persistence strategies

**Dashboard Performance**
- Enable query caching
- Use data pagination for large datasets
- Implement data aggregation for historical data

## 📚 API Reference

### Database Logger

```python
from ghostai.database_logger import get_database_logger

db_logger = get_database_logger()

# Log a scan result
db_logger.log_scan_result(
    text="input text",
    result={"score": 0.8, "flags": ["presidio"]},
    session_id="session-123",
    user_agent="my-app/1.0",
    ip_address="192.168.1.100"
)

# Get recent scans
recent_scans = db_logger.get_recent_scans(limit=100)

# Cleanup old records
deleted_count = db_logger.cleanup_old_records(days=30)
```

### Redis Cache

```python
from ghostai.redis_cache import get_redis_cache

cache = get_redis_cache()

# Cache a scan result
cache.cache_scan_result("session-123", result, ttl=3600)

# Get cached results
cached_results = cache.get_recent_scans("session-123", limit=10)

# Get cache statistics
stats = cache.get_cache_stats()
```

## 🎯 Future Enhancements

### Planned Features
- **Real-time Alerts**: Slack/email notifications for high-risk scans
- **Machine Learning**: Anomaly detection and pattern recognition
- **Advanced Analytics**: Custom dashboards and reporting
- **API Rate Limiting**: Built-in rate limiting and throttling
- **Multi-tenant Support**: Isolated data per organization

### Scalability Improvements
- **Horizontal Scaling**: Multiple dashboard instances
- **Database Sharding**: Partition data by time or organization
- **Message Queues**: Async processing with Celery/RQ
- **CDN Integration**: Cached dashboard assets

## 📞 Support

For issues and questions:
- **Documentation**: This file and inline code comments
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: support@ghostai-dlp.com

---

**Built with ❤️ for Enterprise Security**

[⭐ Star us on GitHub](https://github.com/your-org/ghostai-dlp-sdk) • [📖 Read the docs](https://docs.ghostai-dlp.com) • [🐛 Report bugs](https://github.com/your-org/ghostai-dlp-sdk/issues)
