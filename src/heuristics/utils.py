from typing import List
from collections import Counter
from math import log
from .types.redactor_types import RedactedFinding, Finding
from typing import List

def noise_or(scores: List[float]) -> float:
    """Fuse component scores into [0,1] with diminishing returns."""
    product = 1.0
    for s in scores:
        product *= (1 - max(0.0, min(1.0, s)))
    return 1 - product

def entropy(text: str) -> float:
    """Return global entropy estimate (used by entropy_shape detector)."""
    counts = Counter(text)
    frequencies = ((i / len(text)) for i in counts.values())
    H = - sum(f * log(f, 2) for f in frequencies)
    H0, Hmax = 3.5, 6.0
    if H <= H0:
        return 0.0
    return min(1.0, (H - H0) / (Hmax - H0))