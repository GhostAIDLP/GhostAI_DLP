from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, Float, TIMESTAMP, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text

Base = declarative_base()

class DlpFinding(Base):
    __tablename__ = "dlp_findings"
    id = Column(Integer, primary_key=True)
    
    # Legacy fields (for batch uploads)
    repo = Column(Text)
    file_path = Column(Text)
    detector = Column(Text)
    score = Column(Float)
    reasons = Column(JSONB)
    severity = Column(Text)
    line_count = Column(Integer)
    avg_line_len = Column(Float)
    max_line_len = Column(Integer)
    
    # New real-time logging fields
    session_id = Column(String(255), index=True)  # For tracking user sessions
    input_hash = Column(String(64), index=True)   # SHA256 hash of input text
    flags = Column(JSONB)                         # List of triggered flags
    latency_ms = Column(Float)                    # Scan latency in milliseconds
    environment = Column(String(50))              # "docker", "local", "cloud", etc.
    user_agent = Column(Text)                     # Client user agent
    ip_address = Column(String(45))               # Client IP (IPv4/IPv6)
    encrypted_reasons = Column(Text)              # Encrypted breakdown data
    is_encrypted = Column(Boolean, default=False) # Flag for encrypted data
    
    created_at = Column(TIMESTAMP, server_default=text("NOW()"), index=True)