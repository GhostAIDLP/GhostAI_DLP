"""
SQLite database logging utility for GhostAI firewall SDK.
Handles real-time logging of scan results to SQLite for local development.
"""

import hashlib
import json
import os
import time
import uuid
import sqlite3
from typing import Dict, Any, Optional
from loguru import logger


class DatabaseLogger:
    """Handles database logging for firewall scan results using SQLite."""
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize SQLite database logger.
        
        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path or os.getenv(
            "DATABASE_URL", 
            "data/ghostai_firewall.db"
        )
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        # Initialize database connection
        try:
            self._init_database()
            logger.info("SQLite database logger initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize database logger: {}", e)
            raise
    
    def _init_database(self):
        """Initialize SQLite database and create tables."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create dlp_findings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dlp_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_id TEXT,
            user_agent TEXT,
            ip_address TEXT,
            input_hash TEXT NOT NULL,
            score REAL NOT NULL,
            flags TEXT NOT NULL,
            breakdown TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            environment TEXT DEFAULT 'local'
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON dlp_findings(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_score ON dlp_findings(score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON dlp_findings(session_id)')
        
        conn.commit()
        conn.close()
    
    def _hash_input(self, text: str) -> str:
        """Hash input text for privacy."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    def log_scan_result(
        self,
        text: str,
        result: Dict[str, Any],
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log a scan result to the database.
        
        Args:
            text: Original input text
            result: Scan result dictionary
            session_id: Optional session identifier
            user_agent: Optional user agent string
            ip_address: Optional IP address
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Prepare data
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            input_hash = self._hash_input(text)
            flags = json.dumps(result.get('flags', []))
            breakdown = json.dumps(result.get('breakdown', []))
            latency_ms = result.get('latency_ms', 0.0)
            
            # Insert record (without environment column for compatibility)
            cursor.execute('''
            INSERT INTO dlp_findings 
            (timestamp, session_id, user_agent, ip_address, input_hash, 
             score, flags, breakdown, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                session_id or 'unknown',
                user_agent or 'unknown',
                ip_address or 'unknown',
                input_hash,
                result.get('score', 0.0),
                flags,
                breakdown,
                latency_ms
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error("Database error while logging scan result: {}", e)
            # Don't raise - logging failures shouldn't break the scan


def get_database_logger() -> DatabaseLogger:
    """Get a database logger instance."""
    return DatabaseLogger()
