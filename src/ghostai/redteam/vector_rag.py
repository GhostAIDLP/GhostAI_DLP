"""
Vector RAG Pipeline for Continuous firewall Learning
Uses vector embeddings and k-nearest neighbors to learn from attack patterns.
"""

import os
import json
import numpy as np
import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
import pickle
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

@dataclass
class AttackCluster:
    """Cluster of similar attacks."""
    cluster_id: int
    attacks: List[str]
    centroid: np.ndarray
    success_rate: float
    common_patterns: List[str]
    last_updated: datetime

@dataclass
class LearningInsight:
    """Insight learned from attack analysis."""
    insight_type: str
    content: str
    confidence: float
    supporting_evidence: List[str]
    timestamp: datetime
    applied: bool

class VectorRAGPipeline:
    """
    Vector RAG pipeline for continuous learning from firewall attacks.
    """
    
    def __init__(self, db_path: str = "data/vector_rag.db", vector_dim: int = 2000):
        self.db_path = db_path
        self.vector_dim = vector_dim
        self.vectorizer = TfidfVectorizer(
            max_features=vector_dim,
            ngram_range=(1, 4),
            analyzer='char_wb',  # FIXED: Better for multilingual
            stop_words=None,  # FIXED: No language-specific stop words
            lowercase=True,
            strip_accents='unicode'
        )
        self.knn_model = None
        self.cluster_model = None
        
        # FIXED: Add mBERT for multilingual support
        try:
            self.classifier = pipeline("text-classification", model="xlm-roberta-base")
            self.tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
            self.model = AutoModel.from_pretrained("xlm-roberta-base")
            self.multilingual_enabled = True
        except Exception as e:
            print(f"Warning: mBERT not available: {e}")
            self.classifier = None
            self.tokenizer = None
            self.model = None
            self.multilingual_enabled = False
        
        self.fitted = False  # Track TF-IDF fit status
        self.attack_vectors = None
        self.attack_clusters: List[AttackCluster] = []
        self.learning_insights: List[LearningInsight] = []
        
        self._init_database()
        self._load_existing_data()
    
    def _init_database(self):
        """Initialize vector RAG database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Attack vectors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attack_text TEXT NOT NULL,
                vector BLOB NOT NULL,
                cluster_id INTEGER,
                success BOOLEAN NOT NULL,
                timestamp DATETIME NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Attack clusters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id INTEGER UNIQUE NOT NULL,
                attacks TEXT NOT NULL,
                centroid BLOB NOT NULL,
                success_rate REAL NOT NULL,
                common_patterns TEXT NOT NULL,
                last_updated DATETIME NOT NULL
            )
        ''')
        
        # Learning insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL NOT NULL,
                supporting_evidence TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                applied BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Pattern effectiveness table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_effectiveness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                success_rate REAL NOT NULL,
                last_updated DATETIME NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_existing_data(self):
        """Load existing data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load attack vectors
        cursor.execute('SELECT attack_text, vector, cluster_id, success, timestamp FROM attack_vectors')
        rows = cursor.fetchall()
        
        if rows:
            attack_texts = [row[0] for row in rows]
            vectors = [pickle.loads(row[1]) for row in rows]
            cluster_ids = [row[2] for row in rows]
            successes = [row[3] for row in rows]
            timestamps = [datetime.fromisoformat(row[4]) for row in rows]
            
            # Fit vectorizer
            self.vectorizer.fit(attack_texts)
            self.attack_vectors = np.array(vectors)
            
            # Build KNN model
            self.knn_model = NearestNeighbors(n_neighbors=min(10, len(vectors)), metric='cosine')
            self.knn_model.fit(self.attack_vectors)
            
            # Load clusters
            self._load_clusters()
        
        conn.close()
    
    def _load_clusters(self):
        """Load attack clusters from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM attack_clusters')
        rows = cursor.fetchall()
        
        for row in rows:
            cluster = AttackCluster(
                cluster_id=row[1],
                attacks=json.loads(row[2]),
                centroid=pickle.loads(row[3]),
                success_rate=row[4],
                common_patterns=json.loads(row[5]),
                last_updated=datetime.fromisoformat(row[6])
            )
            self.attack_clusters.append(cluster)
        
        conn.close()
    
    def detect_multilingual_threat(self, text: str) -> Dict[str, Any]:
        """Detect threats in multilingual text using pattern matching."""
        # Detect language (simple heuristic)
        language = "en"  # default
        if any(word in text.lower() for word in ["ignorar", "instrucciones", "secretos", "anterior"]):
            language = "es"
        elif any(word in text.lower() for word in ["ignorer", "instructions", "secrets", "précédentes"]):
            language = "fr"
        elif any(word in text.lower() for word in ["ignorare", "istruzioni", "segreti", "precedenti"]):
            language = "it"
        
        # Simple threat detection based on keywords
        threat_keywords = [
            "ignore", "ignorar", "ignorer", "ignorare",
            "instructions", "instrucciones", "instructions", "istruzioni",
            "secrets", "secretos", "secrets", "segreti",
            "previous", "anterior", "précédentes", "precedenti",
            "tell me", "dime", "dis-moi", "dimmi"
        ]
        
        threat_score = 0.0
        text_lower = text.lower()
        
        for keyword in threat_keywords:
            if keyword in text_lower:
                threat_score += 0.2
        
        # Boost for multilingual jailbreak patterns
        if language != "en" and any(word in text_lower for word in ["ignore", "ignorar", "ignorer", "ignorare"]):
            threat_score += 0.3
        
        threat_score = min(1.0, threat_score)
        
        return {
            "threat_score": threat_score,
            "language": language,
            "confidence": threat_score,
            "multilingual": language != "en"
        }

    def add_attack(self, attack_text: str, success: bool, metadata: Dict[str, Any] = None):
        """Add a new attack to the vector RAG system."""
        if metadata is None:
            metadata = {}
        
        # Vectorize the attack
        if not self.fitted:
            # FIXED: Fit TF-IDF on first attack
            attack_vector = self.vectorizer.fit_transform([attack_text]).toarray()[0]
            self.fitted = True
            self.attack_vectors = np.array([attack_vector])
        else:
            # Add to existing vectors - ensure same dimensions
            attack_vector = self.vectorizer.transform([attack_text]).toarray()[0]
            # Pad or truncate to match existing dimensions
            if len(attack_vector) != self.attack_vectors.shape[1]:
                if len(attack_vector) < self.attack_vectors.shape[1]:
                    # Pad with zeros
                    attack_vector = np.pad(attack_vector, (0, self.attack_vectors.shape[1] - len(attack_vector)))
                else:
                    # Truncate
                    attack_vector = attack_vector[:self.attack_vectors.shape[1]]
            self.attack_vectors = np.vstack([self.attack_vectors, attack_vector])
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attack_vectors (attack_text, vector, success, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            attack_text,
            pickle.dumps(attack_vector),
            success,
            datetime.now().isoformat(),
            json.dumps(metadata)
        ))
        
        conn.commit()
        conn.close()
        
        # Rebuild KNN model
        self._rebuild_knn_model()
        
        # Update clusters
        self._update_clusters()
    
    def _rebuild_knn_model(self):
        """Rebuild KNN model with updated vectors."""
        if self.attack_vectors is None or len(self.attack_vectors) < 2:
            return
        
        self.knn_model = NearestNeighbors(
            n_neighbors=min(10, len(self.attack_vectors)), 
            metric='cosine'
        )
        self.knn_model.fit(self.attack_vectors)
    
    def _update_clusters(self):
        """Update attack clusters using DBSCAN."""
        if self.attack_vectors is None or len(self.attack_vectors) < 5:
            return
        
        # Use DBSCAN for clustering
        self.cluster_model = DBSCAN(eps=0.3, min_samples=3, metric='cosine')
        cluster_labels = self.cluster_model.fit_predict(self.attack_vectors)
        
        # Update clusters
        self.attack_clusters = []
        
        for cluster_id in set(cluster_labels):
            if cluster_id == -1:  # Noise points
                continue
            
            # Get attacks in this cluster
            cluster_mask = cluster_labels == cluster_id
            cluster_attacks = []
            cluster_successes = []
            
            # Get attack texts and success rates from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT attack_text, success FROM attack_vectors ORDER BY id')
            rows = cursor.fetchall()
            conn.close()
            
            for i, (text, success) in enumerate(rows):
                if i < len(cluster_labels) and cluster_labels[i] == cluster_id:
                    cluster_attacks.append(text)
                    cluster_successes.append(success)
            
            if cluster_attacks:
                # Calculate cluster statistics
                success_rate = sum(cluster_successes) / len(cluster_successes)
                centroid = np.mean(self.attack_vectors[cluster_mask], axis=0)
                
                # Find common patterns
                common_patterns = self._extract_common_patterns(cluster_attacks)
                
                cluster = AttackCluster(
                    cluster_id=cluster_id,
                    attacks=cluster_attacks,
                    centroid=centroid,
                    success_rate=success_rate,
                    common_patterns=common_patterns,
                    last_updated=datetime.now()
                )
                
                self.attack_clusters.append(cluster)
        
        # Save clusters to database
        self._save_clusters()
    
    def _extract_common_patterns(self, attacks: List[str]) -> List[str]:
        """Extract common patterns from a cluster of attacks."""
        from collections import Counter
        import re
        
        # Extract n-grams
        all_bigrams = []
        all_trigrams = []
        
        for attack in attacks:
            tokens = re.findall(r'\b\w+\b', attack.lower())
            
            # Bigrams
            for i in range(len(tokens) - 1):
                all_bigrams.append(f"{tokens[i]} {tokens[i+1]}")
            
            # Trigrams
            for i in range(len(tokens) - 2):
                all_trigrams.append(f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}")
        
        # Find most common patterns
        bigram_counts = Counter(all_bigrams)
        trigram_counts = Counter(all_trigrams)
        
        common_patterns = []
        
        # Add most common bigrams
        for pattern, count in bigram_counts.most_common(3):
            if count >= 2:  # At least 2 occurrences
                common_patterns.append(pattern)
        
        # Add most common trigrams
        for pattern, count in trigram_counts.most_common(2):
            if count >= 2:  # At least 2 occurrences
                common_patterns.append(pattern)
        
        return common_patterns
    
    def _save_clusters(self):
        """Save clusters to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing clusters
        cursor.execute('DELETE FROM attack_clusters')
        
        # Save new clusters
        for cluster in self.attack_clusters:
            cursor.execute('''
                INSERT INTO attack_clusters 
                (cluster_id, attacks, centroid, success_rate, common_patterns, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                cluster.cluster_id,
                json.dumps(cluster.attacks),
                pickle.dumps(cluster.centroid),
                cluster.success_rate,
                json.dumps(cluster.common_patterns),
                cluster.last_updated.isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def find_similar_attacks(self, text: str, k: int = 5) -> List[Tuple[str, float]]:
        """Find similar attacks using k-nearest neighbors."""
        if self.knn_model is None or self.attack_vectors is None:
            return []
        
        # Vectorize input text
        text_vector = self.vectorizer.transform([text]).toarray()
        
        # Find similar attacks
        distances, indices = self.knn_model.kneighbors(text_vector)
        
        # Get attack texts from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT attack_text FROM attack_vectors ORDER BY id')
        attack_texts = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        similar_attacks = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(attack_texts):
                similarity = 1 - dist  # Convert distance to similarity
                similar_attacks.append((attack_texts[idx], similarity))
        
        return similar_attacks[:k]
    
    def find_attack_clusters(self, text: str, threshold: float = 0.7) -> List[AttackCluster]:
        """Find attack clusters similar to the input text."""
        if not self.attack_clusters:
            return []
        
        # Vectorize input text
        text_vector = self.vectorizer.transform([text]).toarray()[0]
        
        similar_clusters = []
        for cluster in self.attack_clusters:
            # Calculate similarity to cluster centroid
            similarity = cosine_similarity([text_vector], [cluster.centroid])[0][0]
            
            if similarity >= threshold:
                similar_clusters.append(cluster)
        
        # Sort by similarity
        similar_clusters.sort(key=lambda c: cosine_similarity([text_vector], [c.centroid])[0][0], reverse=True)
        
        return similar_clusters
    
    def generate_insights(self) -> List[LearningInsight]:
        """Generate learning insights from attack analysis."""
        insights = []
        
        if not self.attack_clusters:
            return insights
        
        # Analyze cluster effectiveness
        for cluster in self.attack_clusters:
            if len(cluster.attacks) >= 3:  # At least 3 attacks in cluster
                insight = LearningInsight(
                    insight_type="cluster_effectiveness",
                    content=f"Cluster {cluster.cluster_id} has {cluster.success_rate:.1%} success rate with {len(cluster.attacks)} attacks",
                    confidence=0.8,
                    supporting_evidence=cluster.common_patterns,
                    timestamp=datetime.now(),
                    applied=False
                )
                insights.append(insight)
        
        # Analyze pattern effectiveness
        pattern_stats = self._analyze_pattern_effectiveness()
        
        for pattern, stats in pattern_stats.items():
            if stats['total_count'] >= 5:  # At least 5 uses
                insight = LearningInsight(
                    insight_type="pattern_effectiveness",
                    content=f"Pattern '{pattern}' has {stats['success_rate']:.1%} success rate ({stats['success_count']}/{stats['total_count']})",
                    confidence=0.9,
                    supporting_evidence=[pattern],
                    timestamp=datetime.now(),
                    applied=False
                )
                insights.append(insight)
        
        # Analyze temporal trends
        temporal_insights = self._analyze_temporal_trends()
        insights.extend(temporal_insights)
        
        # Save insights
        self._save_insights(insights)
        
        return insights
    
    def _analyze_pattern_effectiveness(self) -> Dict[str, Dict[str, Any]]:
        """Analyze effectiveness of different attack patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT attack_text, success FROM attack_vectors')
        rows = cursor.fetchall()
        conn.close()
        
        pattern_stats = {}
        
        for attack_text, success in rows:
            # Extract patterns (simple word-based)
            words = attack_text.lower().split()
            
            # Check for common attack patterns
            patterns = []
            if any(word in words for word in ['ignore', 'forget', 'override']):
                patterns.append('instruction_override')
            if any(word in words for word in ['pretend', 'act', 'role']):
                patterns.append('role_playing')
            if any(word in words for word in ['emergency', 'life', 'depends']):
                patterns.append('social_engineering')
            if any(word in words for word in ['step', 'first', 'then']):
                patterns.append('multi_step')
            
            for pattern in patterns:
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {'success_count': 0, 'total_count': 0}
                
                pattern_stats[pattern]['total_count'] += 1
                if success:
                    pattern_stats[pattern]['success_count'] += 1
        
        # Calculate success rates
        for pattern in pattern_stats:
            stats = pattern_stats[pattern]
            stats['success_rate'] = stats['success_count'] / stats['total_count']
        
        return pattern_stats
    
    def _analyze_temporal_trends(self) -> List[LearningInsight]:
        """Analyze temporal trends in attacks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT success, timestamp FROM attack_vectors ORDER BY timestamp')
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 10:
            return []
        
        # Analyze recent vs older attacks
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_attacks = [row for row in rows if datetime.fromisoformat(row[1]) > recent_cutoff]
        older_attacks = [row for row in rows if datetime.fromisoformat(row[1]) <= recent_cutoff]
        
        if len(recent_attacks) >= 5 and len(older_attacks) >= 5:
            recent_success_rate = sum(1 for row in recent_attacks if row[0]) / len(recent_attacks)
            older_success_rate = sum(1 for row in older_attacks if row[0]) / len(older_attacks)
            
            if abs(recent_success_rate - older_success_rate) > 0.1:
                trend = "increasing" if recent_success_rate > older_success_rate else "decreasing"
                insight = LearningInsight(
                    insight_type="temporal_trend",
                    content=f"Attack success rate is {trend} (recent: {recent_success_rate:.1%}, older: {older_success_rate:.1%})",
                    confidence=0.7,
                    supporting_evidence=[f"Recent: {len(recent_attacks)} attacks", f"Older: {len(older_attacks)} attacks"],
                    timestamp=datetime.now(),
                    applied=False
                )
                return [insight]
        
        return []
    
    def _save_insights(self, insights: List[LearningInsight]):
        """Save insights to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for insight in insights:
            cursor.execute('''
                INSERT INTO learning_insights 
                (insight_type, content, confidence, supporting_evidence, timestamp, applied)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_type,
                insight.content,
                insight.confidence,
                json.dumps(insight.supporting_evidence),
                insight.timestamp.isoformat(),
                insight.applied
            ))
        
        conn.commit()
        conn.close()
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get attack statistics
        cursor.execute('SELECT COUNT(*), SUM(CASE WHEN success THEN 1 ELSE 0 END) FROM attack_vectors')
        total_attacks, successful_attacks = cursor.fetchone()
        
        # Get cluster statistics
        cursor.execute('SELECT COUNT(*) FROM attack_clusters')
        num_clusters = cursor.fetchone()[0]
        
        # Get insight statistics
        cursor.execute('SELECT COUNT(*), SUM(CASE WHEN applied THEN 1 ELSE 0 END) FROM learning_insights')
        total_insights, applied_insights = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_attacks": total_attacks or 0,
            "successful_attacks": successful_attacks or 0,
            "success_rate": (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0,
            "num_clusters": num_clusters,
            "total_insights": total_insights or 0,
            "applied_insights": applied_insights or 0,
            "vector_dimension": self.vector_dim
        }
