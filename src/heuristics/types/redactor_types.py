from typing import Optional, Dict
from pydantic import BaseModel

# ---- Rule definitions ----
class RedactionRule(BaseModel):
    prefix: Optional[int] = 0
    suffix: Optional[int] = 0
    mask: Optional[str] = "***"
    passthrough: Optional[bool] = False


# ---- Defaults section ----
class RedactionDefaults(BaseModel):
    provider: Dict[str, RedactionRule] = {}
    category: Dict[str, RedactionRule] = {}
    global_: RedactionRule  # rename global -> global_ to avoid keyword clash


# ---- Full config ----
class RedactionConfig(BaseModel):
    rules: Dict[str, RedactionRule] = {}
    defaults: RedactionDefaults


# ---- Finding object (what detectors return) ----
class Finding(BaseModel):
    id: str
    provider: Optional[str]
    category: str
    match: str
    start: Optional[int] = None
    end: Optional[int] = None


# ---- Redacted result (what engine logs/returns) ----
class RedactedFinding(BaseModel):
    id: str
    redacted: str
    severity: Optional[str] = None
    length: Optional[int] = None
