from . import Detector
from typing import Tuple, List, Any, Dict
from heuristics.utils import entropy, noise_or

class EntropyShapeDetector:
    """Entropy + simple shape: high entropy on long text; very long single line."""
    name = "entropy_shape"

    def __init__(self, cfg: Dict[str, Any]):
        self.entropy_len_min = cfg.get("entropy_len_min", 40)
        self.entropy_weight  = cfg.get("entropy_weight", 0.25)
        self.long_line_len   = cfg.get("long_line_len", 200)
        self.shape_weight    = cfg.get("shape_weight", 0.15)    
        
    def score(self, text: str, text_lower: str) -> Tuple[float, List[str]]:
        """Use global entropy and line shape to assign light score; add reasons."""
        """Returns (component_score, reasons)."""
        reasons: List[str] = []
        parts: List[float] = []

        ent = entropy(text)
        if len(text) >= self.entropy_len_min:
            parts.append(min(self.entropy_weight, ent * self.entropy_weight))
            reasons.append(f"entropy:norm={ent:.2f} len={len(text)}")
        
        if "\n" not in text:
            if len(text) >= self.long_line_len:
                parts.append(self.shape_weight)
                reasons.append(f"shape:long_single_line len={len(text)}")
            if len(text) > 0:
                space_ratio = text.count(" ") / len(text)
                if space_ratio < 0.02 and len(text) >= max(80, self.long_line_len // 2):
                    parts.append(min(self.shape_weight, 0.5 * self.shape_weight))
                    reasons.append(f"shape:low_space ratio={space_ratio:.3f} len={len(text)}")

        return noise_or(parts), reasons