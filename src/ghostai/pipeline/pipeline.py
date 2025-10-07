# src/pipeline/pipeline.py
import yaml


from ghostai.scanners.presidio_scanner import PresidioScanner
from ghostai.scanners.trufflehog_scanner import TrufflehogScanner
from ghostai.scanners.prompt_guard2_scanner import PromptGuard2Scanner
from ghostai.scanners.gitleaks_scanner import GitleaksScanner
class Pipeline:
    def __init__(self, config_path: str = "src/config/scanners.yaml", profile: str = "runtime"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # 🔑 pick correct profile (runtime, ci, etc.)
        self.config = config.get("profiles", {}).get(profile, {})
        if not self.config:
            raise ValueError(f"Profile '{profile}' not found in config")

        self.scanners = []
        self._init_scanners()

    def _init_scanners(self):
        cfg = self.config

        if cfg.get("presidio", {}).get("enabled", False):
            self.scanners.append(PresidioScanner(
                anonymize=cfg["presidio"].get("anonymize", True)
            ))

        if cfg.get("trufflehog", {}).get("enabled", False):
            self.scanners.append(TrufflehogScanner())

        if cfg.get("gitleaks", {}).get("enabled", False):
            self.scanners.append(GitleaksScanner())

        if cfg.get("promptguard2", {}).get("enabled", False):
            self.scanners.append(PromptGuard2Scanner(
                threshold=cfg["promptguard2"].get("threshold", 0.8)
            ))

    def run(self, text: str):
        if not self.scanners:
            return {"score": 0.0, "flags": [], "breakdown": []}

        results = [s.scan(text) for s in self.scanners]
        return {
            "score": max(r.score for r in results),
            "flags": [r.name for r in results if r.flagged],
            "breakdown": [r.to_dict() for r in results],
        }
