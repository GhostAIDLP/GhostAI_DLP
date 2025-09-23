from . import Detector
from typing import Tuple, List
from heuristics.types.rule_types import Rule
import re

class KeywordsDetector(Detector):
    """Small keyword tripwire (password, token, secret, apikey, private key, jwt)."""
    name = "keywords"

    def __init__(self, cfg: list[dict]):
        self.rules = self._compile(cfg)

    def _compile(self, cfg: list[dict]) -> None:
        """Prepare keyword list / simple matcher."""
        rules = []
        for rule_dict in cfg:
            rule: Rule = Rule(**rule_dict)
            compiled = re.compile(re.escape(rule.term), re.IGNORECASE) if rule.term else None
            rules.append({"rule": rule, "pattern": compiled})
        return rules