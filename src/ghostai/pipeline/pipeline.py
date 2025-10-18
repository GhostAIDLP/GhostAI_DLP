# src/ghostai/pipeline/pipeline.py
import os
import time
import yaml
from typing import Dict, Any, Optional

from ghostai.scanners.presidio_scanner import PresidioScanner
from ghostai.scanners.trufflehog_scanner import TrufflehogScanner
from ghostai.scanners.prompt_guard2_scanner import PromptGuard2Scanner
from ghostai.scanners.bert_jailbreak_scanner import BERTJailbreakScanner
from ghostai.scanners.gitleaks_scanner import GitleaksScanner
from ghostai.scanners.regex_secrets_scanner import RegexSecretsScanner
from ghostai.scanners.image_exploit_scanner import ImageExploitScanner
from ghostai.scanners.pdf_exploit_scanner import PDFExploitScanner
from ghostai.database_logger_sqlite import get_database_logger

# dynamically compute config path based on THIS file’s position
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "ghostai", "config", "scanners.yaml")

class Pipeline:
    def __init__(self, config_path: str = CONFIG_PATH, profile: str = "runtime", enable_logging: bool = True):
        print(f"[DEBUG] Loading config from: {os.path.abspath(config_path)}")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Config not found at: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.config = config.get("profiles", {}).get(profile, {})
        if not self.config:
            raise ValueError(f"Profile '{profile}' not found in config")

        self.scanners = []
        self.enable_logging = enable_logging
        self.db_logger = get_database_logger() if enable_logging else None
        self._init_scanners()

    def _init_scanners(self):
        cfg = self.config
        if cfg.get("presidio", {}).get("enabled", False):
            self.scanners.append(PresidioScanner(anonymize=cfg["presidio"].get("anonymize", True)))
        if cfg.get("trufflehog", {}).get("enabled", False):
            self.scanners.append(TrufflehogScanner())
        if cfg.get("gitleaks", {}).get("enabled", False):
            self.scanners.append(GitleaksScanner())
        if cfg.get("promptguard2", {}).get("enabled", False):
            self.scanners.append(PromptGuard2Scanner(threshold=cfg["promptguard2"].get("threshold", 0.8)))
        if cfg.get("bert_jailbreak", {}).get("enabled", False):
            self.scanners.append(BERTJailbreakScanner(threshold=cfg["bert_jailbreak"].get("threshold", 0.3)))
        if cfg.get("regex_secrets", {}).get("enabled", False):
            self.scanners.append(RegexSecretsScanner())
        if cfg.get("image_exploit", {}).get("enabled", False):
            self.scanners.append(ImageExploitScanner(threshold=cfg["image_exploit"].get("threshold", 0.7)))
        if cfg.get("pdf_exploit", {}).get("enabled", False):
            self.scanners.append(PDFExploitScanner(threshold=cfg["pdf_exploit"].get("threshold", 0.7)))

    def run(self, text: str, session_id: Optional[str] = None, user_agent: Optional[str] = None, 
            ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Run firewall scan on input text with optional database logging.
        
        Args:
            text: Input text to scan
            session_id: Optional session identifier for tracking
            user_agent: Optional client user agent
            ip_address: Optional client IP address
            
        Returns:
            Dictionary with scan results including score, flags, and breakdown
        """
        start_time = time.time()
        
        if not self.scanners:
            result = {"score": 0.0, "flags": [], "breakdown": {}}
        else:
            results = [s.scan(text) for s in self.scanners]
            # Handle both dict and object results
            scores = []
            flags = []
            breakdown = {}
            
            for i, r in enumerate(results):
                if isinstance(r, dict):
                    scores.append(r.get('score', 0.0))
                    if r.get('flagged', False):
                        flags.append(f"scanner_{i}")
                    breakdown[f"scanner_{i}"] = r
                else:
                    scores.append(getattr(r, 'score', 0.0))
                    if getattr(r, 'flagged', False):
                        flags.append(getattr(r, 'name', f"scanner_{i}"))
                    breakdown[getattr(r, 'name', f"scanner_{i}")] = r.to_dict() if hasattr(r, 'to_dict') else r
            
            result = {
                "score": max(scores) if scores else 0.0,
                "flagged": max(scores) > 0.5 if scores else False,  # Add flagged field
                "flags": flags,
                "breakdown": breakdown,
            }
        
        # Add latency information
        latency_ms = (time.time() - start_time) * 1000
        result["latency_ms"] = latency_ms
        
        # Log to database if enabled
        if self.enable_logging and self.db_logger:
            try:
                self.db_logger.log_scan_result(
                    text=text,
                    result=result,
                    session_id=session_id,
                    user_agent=user_agent,
                    ip_address=ip_address
                )
            except Exception as e:
                # Don't fail the scan if logging fails
                print(f"[WARNING] Failed to log scan result: {e}")
        
        return result
