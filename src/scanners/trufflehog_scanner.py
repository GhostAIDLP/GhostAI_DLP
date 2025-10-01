# src/scanners/trufflehog_scanner.py
import subprocess, json
from .base import BaseScanner, ScanResult

class TrufflehogScanner(BaseScanner):
    def scan(self, text: str) -> ScanResult:
        """
        Run TruffleHog regex mode against input text.
        Captures potential secrets and normalizes to ScanResult.
        """
        try:
            result = subprocess.run(
                ["trufflehog", "regex", "--json", "-"],
                input=text.encode("utf-8"),
                capture_output=True,
                check=False
            )

            findings = []
            for line in result.stdout.decode().splitlines():
                if line.strip():
                    try:
                        findings.append(json.loads(line))
                    except json.JSONDecodeError:
                        findings.append({"raw": line})

            return ScanResult(
                name="trufflehog",
                flagged=bool(findings),
                score=1.0 if findings else 0.0,
                reasons=findings
            )

        except Exception as e:
            return ScanResult("trufflehog", flagged=False, reasons=[str(e)])
