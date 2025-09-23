from typing import Tuple, List, Pattern
from heuristics.types.rule_types import Rule
import re
from heuristics.utils import noise_or

class Detector:
    """Base interface for detectors. Children override _compile() and score()."""
    name: str

    def __init__(self, cfg: list[dict]):
        self.rules = self._compile(cfg)

    def _compile(self, cfg: list[dict]) -> list[dict]:
        rules = []
        for rule_dict in cfg:
            rule: Rule = Rule(**rule_dict)
            compiled = re.compile(rule.regex) if rule.regex else None
            rules.append({"rule": rule, "pattern": compiled})
        return rules

    def score(self, text: str, text_lower: str) -> Tuple[float, List[str]]:
        """Return medium score if patterns present; include length/shape in reasons."""
        scores, reasons = [], []
        for entry in self.rules:
            pattern: Pattern = entry["pattern"]
            rule: Rule = entry["rule"]
            if not pattern:
                continue
            m = pattern.search(text)
            if m:
                scores.append(rule.weight)
                start, end = m.span()
                reasons.append(f"{self.name}:{rule.id} offset={start} len={end-start}")
        return (noise_or(scores), reasons)
