# src/scanners/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ScanResult:
    def __init__(self, name: str, flagged: bool, score: float = 0.0, reasons: List[Any] = None):
        self.name = name
        self.flagged = flagged
        self.score = score
        self.reasons = reasons or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "flagged": self.flagged,
            "score": self.score,
            "reasons": self.reasons,
        }

class BaseScanner(ABC):
    @abstractmethod
    def scan(self, text: str) -> ScanResult:
        """Run the scanner against input text"""
        pass
