# 🏗️ GhostAI Architecture Overview

> **System design, component architecture, and data flow patterns**

## 🎯 System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GhostAI Security Firewall                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│  │   Client Apps   │    │   Web Dashboard │    │   API Gateway   │        │
│  │   (Mobile/Web)  │    │   (Streamlit)   │    │   (REST API)    │        │
│  └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘        │
│            │                      │                      │                │
│            └──────────────────────┼──────────────────────┘                │
│                                   │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐    │
│  │                    Security Firewall Layer                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │    │
│  │  │ Rate        │  │ Request     │  │ IP          │  │ Size    │  │    │
│  │  │ Limiting    │  │ Validation  │  │ Blocking    │  │ Limits  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │    │
│  └─────────────────────────────────┬─────────────────────────────────┘    │
│                                   │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐    │
│  │                    Multi-Scanner Pipeline                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │    │
│  │  │ BERT        │  │ Presidio    │  │ Regex       │  │ Image   │  │    │
│  │  │ Jailbreak   │  │ PII         │  │ Secrets     │  │ Exploit │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │    │
│  │  ┌─────────────┐  ┌─────────────┐                                │    │
│  │  │ PDF         │  │ Custom      │                                │    │
│  │  │ Exploit     │  │ Scanners    │                                │    │
│  │  └─────────────┘  └─────────────┘                                │    │
│  └─────────────────────────────────┬─────────────────────────────────┘    │
│                                   │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐    │
│  │                    AI/ML Processing Layer                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │    │
│  │  │ BERT Model  │  │ TF-IDF      │  │ K-NN        │  │ DBSCAN  │  │    │
│  │  │ Inference   │  │ Vectorizer  │  │ Clustering  │  │ Clust.  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │    │
│  └─────────────────────────────────┬─────────────────────────────────┘    │
│                                   │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐    │
│  │                    Continuous Learning Layer                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │    │
│  │  │ Vector RAG  │  │ Red Team    │  │ Pattern     │  │ Model   │  │    │
│  │  │ Pipeline    │  │ Engine      │  │ Evolution   │  │ Updates │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │    │
│  └─────────────────────────────────┬─────────────────────────────────┘    │
│                                   │                                       │
│  ┌─────────────────────────────────▼─────────────────────────────────┐    │
│  │                    Data & Storage Layer                           │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │    │
│  │  │ SQLite      │  │ Redis       │  │ File        │  │ Logs    │  │    │
│  │  │ Database    │  │ Cache       │  │ System      │  │ Storage │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

### Request Processing Pipeline
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Request Lifecycle                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Client Request                                                          │
│     ┌─────────────────┐                                                     │
│     │ HTTP POST       │ ──────────────────────────────────────────────────┐ │
│     │ /v1/chat/       │                                                 │ │
│     │ completions     │                                                 │ │
│     └─────────────────┘                                                 │ │
│                                                                         │ │
│  2. Firewall Layer                                                      │ │
│     ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │ │
│     │ Rate Limiting   │───▶│ Request         │───▶│ IP Blocking     │   │ │
│     │ (1000/min)      │    │ Validation      │    │ (Blacklist)     │   │ │
│     └─────────────────┘    └─────────────────┘    └─────────────────┘   │ │
│                                                                         │ │
│  3. Scanner Pipeline                                                     │ │
│     ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │ │
│     │ BERT Jailbreak  │───▶│ Presidio PII    │───▶│ Regex Secrets   │   │ │
│     │ (93.8% acc)     │    │ (100% acc)      │    │ (100% acc)      │   │ │
│     └─────────────────┘    └─────────────────┘    └─────────────────┘   │ │
│     ┌─────────────────┐    ┌─────────────────┐                          │ │
│     │ Image Exploit   │───▶│ PDF Exploit     │                          │ │
│     │ (URL detection) │    │ (JS detection)  │                          │ │
│     └─────────────────┘    └─────────────────┘                          │ │
│                                                                         │ │
│  4. Decision Engine                                                      │ │
│     ┌─────────────────┐                                                 │ │
│     │ Threat Score    │ ──▶ BLOCK (403) or ALLOW (200)                 │ │
│     │ Aggregation     │                                                 │ │
│     └─────────────────┘                                                 │ │
│                                                                         │ │
│  5. Response Processing                                                  │ │
│     ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │ │
│     │ Log to DB       │───▶│ Update Cache    │───▶│ Send Response   │   │ │
│     │ (SQLite)        │    │ (Redis)         │    │ (Client)        │   │ │
│     └─────────────────┘    └─────────────────┘    └─────────────────┘   │ │
│                                                                         │ │
│  6. Learning Update                                                     │ │
│     ┌─────────────────┐                                                 │ │
│     │ Vector RAG      │ ──▶ Update patterns and models                 │ │
│     │ Pipeline        │                                                 │ │
│     └─────────────────┘                                                 │ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🧩 Component Architecture

### 1. Security Firewall Layer
```python
class GhostAIFirewall:
    """
    Core firewall component that orchestrates security checks
    """
    def __init__(self):
        self.rate_limiter = RateLimiter(1000, 60)  # 1000 req/min
        self.ip_blocker = IPBlocker()
        self.scanner_pipeline = ScannerPipeline()
        self.learning_engine = LearningEngine()
    
    def process_request(self, request):
        # 1. Rate limiting check
        if not self.rate_limiter.allow_request(request):
            return self._block_request("Rate limit exceeded")
        
        # 2. IP blocking check
        if self.ip_blocker.is_blocked(request.ip):
            return self._block_request("IP blocked")
        
        # 3. Scanner pipeline execution
        scan_result = self.scanner_pipeline.scan(request.content)
        
        # 4. Decision making
        if scan_result.threat_score > self.threshold:
            return self._block_request("Threat detected")
        
        # 5. Learning update
        self.learning_engine.update_patterns(request, scan_result)
        
        return self._allow_request(request)
```

### 2. Multi-Scanner Pipeline
```python
class ScannerPipeline:
    """
    Orchestrates multiple security scanners in parallel
    """
    def __init__(self):
        self.scanners = [
            BERTJailbreakScanner(threshold=0.5),
            PresidioScanner(threshold=0.9),
            RegexSecretScanner(threshold=0.8),
            ImageExploitScanner(threshold=0.7),
            PDFExploitScanner(threshold=0.6)
        ]
    
    def scan(self, content):
        results = []
        for scanner in self.scanners:
            result = scanner.scan(content)
            results.append(result)
        
        # Aggregate results
        return self._aggregate_results(results)
```

### 3. AI/ML Processing Layer
```python
class AIMLProcessor:
    """
    Handles AI/ML model inference and pattern matching
    """
    def __init__(self):
        self.bert_model = load_bert_model()
        self.tfidf_vectorizer = TfidfVectorizer()
        self.knn_classifier = KNeighborsClassifier()
        self.dbscan_clusterer = DBSCAN()
    
    def process_text(self, text):
        # 1. BERT inference
        bert_score = self.bert_model.predict_proba(text)
        
        # 2. TF-IDF vectorization
        tfidf_vector = self.tfidf_vectorizer.transform([text])
        
        # 3. K-NN classification
        knn_score = self.knn_classifier.predict_proba(tfidf_vector)
        
        # 4. DBSCAN clustering
        cluster_id = self.dbscan_clusterer.fit_predict(tfidf_vector)
        
        return self._combine_scores(bert_score, knn_score, cluster_id)
```

## 🔗 Component Interactions

### Inter-Component Communication
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Component Interaction Map                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Client    │───▶│  Firewall   │───▶│  Scanner    │                    │
│  │   Request   │    │   Layer     │    │  Pipeline   │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│                           │                      │                        │
│                           ▼                      ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Response  │◀───│  Decision   │◀───│  AI/ML      │                    │
│  │   Handler   │    │   Engine    │    │  Processor  │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│                           │                      │                        │
│                           ▼                      ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Logging   │◀───│  Learning   │◀───│  Vector     │                    │
│  │   System    │    │   Engine    │    │  RAG        │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│                           │                      │                        │
│                           ▼                      ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Database  │◀───│   Cache     │◀───│   Storage   │                    │
│  │   (SQLite)  │    │   (Redis)   │    │   System    │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Patterns
1. **Synchronous Processing**: Real-time request processing with immediate response
2. **Asynchronous Learning**: Background pattern updates and model improvements
3. **Caching Strategy**: Redis-based caching for frequently accessed patterns
4. **Batch Processing**: Periodic model retraining and pattern optimization

## 🏛️ Design Patterns

### 1. Pipeline Pattern
```python
class Pipeline:
    """
    Generic pipeline for processing data through multiple stages
    """
    def __init__(self, stages):
        self.stages = stages
    
    def process(self, data):
        for stage in self.stages:
            data = stage.process(data)
        return data
```

### 2. Strategy Pattern
```python
class ScannerStrategy:
    """
    Strategy pattern for different scanner implementations
    """
    def scan(self, content):
        raise NotImplementedError

class BERTJailbreakScanner(ScannerStrategy):
    def scan(self, content):
        return self.bert_model.predict(content)

class PresidioScanner(ScannerStrategy):
    def scan(self, content):
        return self.presidio_analyzer.analyze(content)
```

### 3. Observer Pattern
```python
class LearningObserver:
    """
    Observer pattern for learning system updates
    """
    def update(self, event):
        if event.type == "new_threat":
            self.update_patterns(event.data)
        elif event.type == "false_positive":
            self.adjust_thresholds(event.data)
```

## 📊 Performance Architecture

### Caching Strategy
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Caching Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   L1 Cache  │    │   L2 Cache  │    │   L3 Cache  │                    │
│  │   (Memory)  │    │   (Redis)   │    │   (Disk)    │                    │
│  │   <1ms      │    │   ~5ms      │    │   ~50ms     │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│         │                   │                   │                        │
│         ▼                   ▼                   ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Hot       │    │   Warm       │   │   Cold       │                    │
│  │   Patterns  │    │   Patterns   │   │   Patterns   │                    │
│  │   (99% hit) │    │   (80% hit)  │   │   (20% hit)  │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Load Balancing
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Load Balancing Strategy                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Load      │    │   Health    │    │   Failover  │                    │
│  │   Balancer  │───▶│   Checker   │───▶│   Manager   │                    │
│  │   (Nginx)   │    │   (Redis)   │    │   (Custom)  │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│         │                   │                   │                        │
│         ▼                   ▼                   ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Firewall  │    │   Firewall  │    │   Firewall  │                    │
│  │   Instance  │    │   Instance  │    │   Instance  │                    │
│  │   #1        │    │   #2        │    │   #3        │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration Architecture

### Environment-Specific Configs
```yaml
# Development
development:
  debug: true
  log_level: DEBUG
  cache_ttl: 300
  rate_limit: 1000

# Staging
staging:
  debug: false
  log_level: INFO
  cache_ttl: 600
  rate_limit: 5000

# Production
production:
  debug: false
  log_level: WARNING
  cache_ttl: 3600
  rate_limit: 10000
```

### Feature Flags
```python
class FeatureFlags:
    """
    Feature flag system for gradual rollouts
    """
    def __init__(self):
        self.flags = {
            "enable_learning": True,
            "enable_redis_cache": True,
            "enable_multilingual": True,
            "enable_image_scanning": True,
            "enable_pdf_scanning": True
        }
    
    def is_enabled(self, feature):
        return self.flags.get(feature, False)
```

## 🚀 Scalability Architecture

### Horizontal Scaling
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Horizontal Scaling                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   API       │    │   API       │    │   API       │                    │
│  │   Gateway   │    │   Gateway   │    │   Gateway   │                    │
│  │   (Node 1)  │    │   (Node 2)  │    │   (Node 3)  │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│         │                   │                   │                        │
│         ▼                   ▼                   ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│  │   Firewall  │    │   Firewall  │    │   Firewall  │                    │
│  │   Instance  │    │   Instance  │    │   Instance  │                    │
│  │   (Pod 1)   │    │   (Pod 2)   │    │   (Pod 3)   │                    │
│  └─────────────┘    └─────────────┘    └─────────────┘                    │
│         │                   │                   │                        │
│         └───────────────────┼───────────────────┘                        │
│                             ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Shared Services                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │  │
│  │  │   Redis     │  │   Database  │  │   Storage   │  │  Logs   │  │  │
│  │  │   Cluster   │  │   Cluster   │  │   Cluster   │  │ Cluster │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Vertical Scaling
- **CPU Scaling**: Multi-core processing for parallel scanner execution
- **Memory Scaling**: Increased cache size and model storage
- **Storage Scaling**: Larger databases and log storage
- **Network Scaling**: Higher bandwidth for increased throughput

---

**Next**: [AI/ML Models](AI_MODELS.md) - Deep dive into the machine learning implementation
