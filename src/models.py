from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text

Base = declarative_base()

class DlpFinding(Base):
    __tablename__ = "dlp_findings"
    id = Column(Integer, primary_key=True)
    repo = Column(Text)
    file_path = Column(Text)
    detector = Column(Text)
    score = Column(Float)
    reasons = Column(JSONB)
    severity = Column(Text)
    line_count = Column(Integer)
    avg_line_len = Column(Float)
    max_line_len = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))