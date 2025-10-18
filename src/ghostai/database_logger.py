"""
Database logging utility for GhostAI firewall SDK.
Handles real-time logging of scan results to PostgreSQL with encryption support.
"""

import hashlib
import json
import os
import time
import uuid
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from models import DlpFinding


class DatabaseLogger:
    """Handles database logging for firewall scan results."""
    
    def __init__(self, database_url: Optional[str] = None, encryption_key: Optional[str] = None):
        """
        Initialize database logger.
        
        Args:
            database_url: PostgreSQL connection string
            encryption_key: Base64-encoded encryption key for sensitive data
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://ghostai:ghostai123@db:5432/ghostai"
        )
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate a new key if none provided (for development)
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            logger.warning("Generated new encryption key. Store this securely: {}", key.decode())
        
        # Initialize database connection
        try:
            self.engine = create_engine(self.database_url, pool_pre_ping=True)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database logger initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize database logger: {}", e)
            self.engine = None
            self.Session = None
    
    def log_scan_result(
        self,
        text: str,
        result: Dict[str, Any],
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        environment: Optional[str] = None
    ) -> bool:
        """
        Log a scan result to the database.
        
        Args:
            text: Input text that was scanned
            result: Scan result dictionary with score, flags, breakdown
            session_id: Optional session identifier
            user_agent: Optional client user agent
            ip_address: Optional client IP address
            environment: Optional environment identifier
            
        Returns:
            True if logging succeeded, False otherwise
        """
        if not self.engine or not self.Session:
            logger.error("Database not initialized, cannot log scan result")
            return False
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Hash input text for privacy
            input_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            
            # Determine environment
            if not environment:
                environment = self._detect_environment()
            
            # Encrypt sensitive breakdown data
            breakdown_data = result.get("breakdown", [])
            encrypted_reasons = None
            is_encrypted = False
            
            if breakdown_data:
                try:
                    breakdown_json = json.dumps(breakdown_data)
                    encrypted_reasons = self.cipher.encrypt(breakdown_json.encode()).decode()
                    is_encrypted = True
                except Exception as e:
                    logger.warning("Failed to encrypt breakdown data: {}", e)
            
            # Create database record
            finding = DlpFinding(
                session_id=session_id,
                input_hash=input_hash,
                score=result.get("score", 0.0),
                flags=result.get("flags", []),
                reasons=breakdown_data if not is_encrypted else None,
                encrypted_reasons=encrypted_reasons,
                is_encrypted=is_encrypted,
                severity=self._determine_severity(result.get("score", 0.0)),
                detector="ghostai",  # Default detector for real-time scans
                environment=environment,
                user_agent=user_agent,
                ip_address=ip_address,
                latency_ms=result.get("latency_ms", 0.0)
            )
            
            # Save to database
            with self.Session() as session:
                session.add(finding)
                session.commit()
                
            logger.debug(
                "Logged scan result: session_id={}, score={}, flags={}",
                session_id, result.get("score"), result.get("flags")
            )
            return True
            
        except SQLAlchemyError as e:
            logger.error("Database error while logging scan result: {}", e)
            return False
        except Exception as e:
            logger.error("Unexpected error while logging scan result: {}", e)
            return False
    
    def _detect_environment(self) -> str:
        """Detect the current environment."""
        if os.path.exists("/.dockerenv"):
            return "docker"
        elif os.getenv("KUBERNETES_SERVICE_HOST"):
            return "kubernetes"
        elif os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            return "aws_lambda"
        elif os.getenv("GOOGLE_CLOUD_PROJECT"):
            return "gcp"
        else:
            return "local"
    
    def _determine_severity(self, score: float) -> str:
        """Determine severity based on score."""
        if score >= 0.9:
            return "Critical"
        elif score >= 0.7:
            return "High"
        elif score >= 0.5:
            return "Medium"
        elif score >= 0.1:
            return "Low"
        else:
            return "Info"
    
    def get_recent_scans(self, limit: int = 100) -> list:
        """Get recent scan results from database."""
        if not self.engine or not self.Session:
            return []
        
        try:
            with self.Session() as session:
                findings = session.query(DlpFinding).order_by(
                    DlpFinding.created_at.desc()
                ).limit(limit).all()
                
                return [
                    {
                        "id": f.id,
                        "session_id": f.session_id,
                        "score": f.score,
                        "flags": f.flags,
                        "severity": f.severity,
                        "environment": f.environment,
                        "latency_ms": f.latency_ms,
                        "created_at": f.created_at.isoformat() if f.created_at else None
                    }
                    for f in findings
                ]
        except Exception as e:
            logger.error("Failed to get recent scans: {}", e)
            return []
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """Clean up records older than specified days."""
        if not self.engine or not self.Session:
            return 0
        
        try:
            from sqlalchemy import text
            with self.Session() as session:
                result = session.execute(
                    text("DELETE FROM dlp_findings WHERE created_at < NOW() - INTERVAL ':days days'"),
                    {"days": days}
                )
                session.commit()
                deleted_count = result.rowcount
                logger.info("Cleaned up {} old records", deleted_count)
                return deleted_count
        except Exception as e:
            logger.error("Failed to cleanup old records: {}", e)
            return 0


# Global instance for easy access
_db_logger = None

def get_database_logger() -> DatabaseLogger:
    """Get the global database logger instance."""
    global _db_logger
    if _db_logger is None:
        _db_logger = DatabaseLogger()
    return _db_logger
