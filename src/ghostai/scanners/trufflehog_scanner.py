# src/scanners/trufflehog_scanner.py
import subprocess, json
from .base import BaseScanner, ScanResult

class TrufflehogScanner(BaseScanner):
    def _run_trufflehog(self, text: str):
        return subprocess.run([...], input=text.encode("utf-8"), capture_output=True, check=False)
    def scan(self, text: str) -> ScanResult:
        """
        Run TruffleHog regex mode against input text.
        Captures potential secrets and normalizes to ScanResult.
        """
        try:
            result = self._run_trufflehog(text)
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
