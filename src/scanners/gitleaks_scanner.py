# src/scanners/gitleaks_scanner.py
import subprocess, json
from .base import BaseScanner, ScanResult

class GitleaksScanner(BaseScanner):
    def scan(self, text: str) -> ScanResult:
        try:
            result = subprocess.run(
                ["gitleaks", "detect", "--no-git", "--report-format=json", "--source=-"],
                input=text.encode("utf-8"),
                capture_output=True,
                check=False
            )
            findings = json.loads(result.stdout.decode() or "[]")
            return ScanResult(
                name="gitleaks",
                flagged=bool(findings),
                score=1.0 if findings else 0.0,
                reasons=findings
            )
        except Exception as e:
            return ScanResult("gitleaks", flagged=False, reasons=[str(e)])
