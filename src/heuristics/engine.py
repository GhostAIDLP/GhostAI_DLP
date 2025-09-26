import time
import unicodedata
from typing import Any, Dict, List
from .types.types import HeuristicsResult, ComponentResult, Severity
from .config import BaseConfig
from .utils import noise_or, entropy
from .detectors.secrets import SecretsDetector
from .detectors.blobs import BlobsDetector
from .detectors.keywords import KeywordsDetector
from .detectors.entropy_shape import EntropyShapeDetector
from .detectors.code_risks import CodeRisksDetector

class HeuristicsEngine:
    """
    V1: preprocess → run 4 detectors → noise_or fuse → severity map.
    Keep fast, deterministic, explainable.
    """

    def __init__(self, detectors: List[Any], cfg: Dict[str, Any]):
        self.detectors = detectors
        self.cfg = cfg
        self.thresholds = cfg.get("severity_thresholds", {"high": 0.80, "medium": 0.50})
        self.reason_limit = cfg.get("reason_limit", 5)
        self.max_reasons_per_detector = cfg.get("max_reasons_per_detector", 3)

    def preprocess(self, text: str) -> tuple[str, str, Dict[str, Any]]:
        """
        Normalize NFC, create lowercase view, truncate to max_input_len.
        Return (text, text_lower, flags) where flags may include 'truncated'.
        """
        flags = {}
        flags["orig_len"] = len(text)
        text_norm = unicodedata.normalize("NFC", text)
        text_norm = text_norm.replace("\r\n", "\n").replace("\r", "\n")
        text_norm = text_norm.strip()
        MAX_TEXT_LEN = BaseConfig.DEFAULTS["max_input_len"]
        text_norm = text_norm[:MAX_TEXT_LEN] if len(text_norm) > MAX_TEXT_LEN else text_norm
        flags["truncated"] = True if len(text_norm) > MAX_TEXT_LEN else False
        text_lower = text_norm.lower()

        flags["line_count"] = text_norm.count('\n') + 1
        flags["max_line_len"] = HeuristicsEngine.get_max_line_len(text_norm)
        flags["avg_line_len"] = HeuristicsEngine.get_average_line_len(text_norm)

        return (text_norm, text_lower, flags)
    

    def _map_severity(self, score: float) -> Severity:
        """Map numeric score to LOW/MEDIUM/HIGH using cfg thresholds."""
        if score > BaseConfig.HIGH_SEVERITY:
            return Severity.HIGH
        elif score > BaseConfig.MEDIUM_SEVERITY:
            return Severity.MEDIUM
        else:
            return Severity.LOW
        
    def score(self, text: str) -> HeuristicsResult:
        """
        Orchestrate:
        - preprocess (DONE)
        - run detectors and collect ComponentResult(name, score, reasons)
        - fuse scores with noise_or
        - cap reasons to reason_limit and include flags (e.g., truncated)
        - return HeuristicsResult(score, severity, breakdown, flags, latency_ms)
        """
        t0 = time.perf_counter()
        text_norm, text_lower, flags = self.preprocess(text)
        

        breakdown: List[ComponentResult] = []
        comp_scores: List[float] = []
        for det in self.detectors:
            try:
                comp_score, reasons = det.score(text_norm, text_lower)
            except Exception as e:
                comp_score, reasons = 0.0, [f"{det.name}:error:{type(e).__name__}"]
            # clamp & trim reasons per detector
            comp_score = max(0.0, min(1.0, comp_score))
            if reasons and self.max_reasons_per_detector:
                reasons = reasons[: self.max_reasons_per_detector]
            breakdown.append(ComponentResult(name=det.name, score=comp_score, reasons=reasons))
            comp_scores.append(comp_score)

        final_score = noise_or(comp_scores)
        severity = self._map_severity(final_score)

        breakdown_sorted = sorted(breakdown, key=lambda c: c.score, reverse=True)

        if self.reason_limit:
            # rebuild with trimmed reasons per detector in priority order
            remaining = self.reason_limit
            trimmed: List[ComponentResult] = []
            for c in breakdown_sorted:
                take = min(len(c.reasons), remaining)
                trimmed.append(ComponentResult(name=c.name, score=c.score, reasons=c.reasons[:take]))
                remaining -= take
                if remaining <= 0:
                    break
            breakdown_final = trimmed
        else:
            breakdown_final = breakdown_sorted


        latency_ms = float((time.perf_counter() - t0) * 1000)
        
        
        return HeuristicsResult(
            score=final_score,
            severity=severity,
            breakdown=breakdown_final,
            flags=flags,
            latency_ms=latency_ms,
        )
        

    def get_average_line_len(text_str: str) -> float:
        lines = text_str.splitlines()
        if not lines:
            return 0.0
        line_lengths = [len(line) for line in lines]
        return sum(line_lengths) / len(line_lengths)
        
    def get_max_line_len(text_str: str) -> int:
        lines = text_str.splitlines()
        if not lines:
            return 0
        line_lengths = [len(line) for line in lines]
        return max(line_lengths)