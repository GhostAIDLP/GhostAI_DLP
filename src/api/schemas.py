from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

# JSON REQUEST/RESPONSE
class Metadata(BaseModel):
    source: str
    lang: str

class HeurisiticsBreakdown(BaseModel):
    name: str
    score: int
    reasons: Optional[List[str]] = []

class Breakdown(BaseModel):
    heuristics: HeurisiticsBreakdown

class Limits(BaseModel):
    latency_ms: int
    path: str

class RiskRequest(BaseModel):
    text: str
    tenant_id: str
    call_back_url: Optional[str] = None
    metadata: Metadata

class RiskSyncResponse(BaseModel):
    request_id: str
    severity: str
    score: int
    breakdown: Breakdown
    flags: Dict[str, Any]
    latency_ms: float
    
class RiskAsyncResponse(BaseModel):
    request_id: str
    status: str
    type: str = "risk_async_ack"


# RULE FORMAT

class Rule (BaseModel):
    id: str
    name: str
    category: str
    weight: float
    default_severity: str
    provider: Optional[str]
    regex: Optional[str]
    term: Optional[str]