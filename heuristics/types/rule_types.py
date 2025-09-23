from typing import Optional
from pydantic import BaseModel

class Rule (BaseModel):
    id: str
    name: str
    category: str
    weight: float
    default_severity: str
    provider: Optional[str] = "generic"
    regex: Optional[str] = None
    term: Optional[str] = None