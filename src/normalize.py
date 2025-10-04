from typing import List, Dict, Any
from scanners.base import ScanResult
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
