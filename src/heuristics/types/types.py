from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Any

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ComponentResult(BaseModel):
    name: str
    score: float
    reasons: List[str]

class HeuristicsResult(BaseModel):
    score: float
    severity: Severity
    breakdown: List[ComponentResult]
    flags: Dict[str, Any]
    latency_ms: float
