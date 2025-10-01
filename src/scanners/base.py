# src/scanners/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ScanResult:
    def __init__(
        self,
        name: str,
        flagged: bool,
        score: float = 0.0,
        reasons: Optional[List[Any]] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.flagged = flagged
        self.score = score
        self.reasons = reasons or []
        self.extra = extra or {}

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "name": self.name,
            "flagged": self.flagged,
            "score": self.score,
            "reasons": self.reasons,
        }
        # Flatten extra fields into the result dict
        if self.extra:
            base.update(self.extra)
        return base


class BaseScanner(ABC):
    @abstractmethod
    def scan(self, text: str) -> ScanResult:
        """Run the scanner against input text"""
        pass
