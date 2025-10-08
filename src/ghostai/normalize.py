from typing import List, Dict, Any
from ghostai.scanners.base import ScanResult

def normalize(results: List[ScanResult]) -> List[Dict[str, Any]]:
    """
    Convert list of ScanResults into unified JSON schema.
    """
    normalized = []
    for r in results:
        normalized.append({
            "detector": r.name,
            "flagged": r.flagged,
            "score": r.score,
            "reasons": r.reasons,
            "extra": r.extra or {},
        })
    return normalized

def normalize_text(text: str) -> str:
    """
    Simple text normalization helper.
    This is a placeholder function for basic text processing.
    """
    return text.strip()
