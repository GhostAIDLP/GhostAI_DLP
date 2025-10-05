# src/scanners/presidio_scanner.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from .base import BaseScanner, ScanResult

class PresidioScanner(BaseScanner):
    def __init__(self, language: str = "en", anonymize: bool = True):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.language = language
        self.anonymize = anonymize

    def scan(self, text: str) -> ScanResult:
        """
        Run Presidio detection and optional anonymization.
        Returns flagged=True if PII entities detected.
        """
        try:
            results = self.analyzer.analyze(text=text, language=self.language)

            if results:
                anonymized_text = None
                if self.anonymize:
                    anonymized = self.anonymizer.anonymize(
                        text=text,
                        analyzer_results=results
                    )
                    anonymized_text = anonymized.text

                return ScanResult(
                    name="presidio",
                    flagged=True,
                    score=1.0,
                    reasons=[r.to_dict() for r in results],
                    extra={"anonymized": anonymized_text}
                )

            # 👇 handle the "no hits" case
            return ScanResult("presidio", flagged=False, score=0.0)

        except Exception as e:
            return ScanResult("presidio", flagged=False, reasons=[str(e)])
