# src/scanners/presidio_scanner.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from .base import BaseScanner, ScanResult
import re

class PresidioScanner(BaseScanner):
    def __init__(self, language: str = "en", anonymize: bool = True):
        # Configure NLP engine with specific recognizers
        provider = NlpEngineProvider()
        nlp_engine = provider.create_engine()
        
        # Create analyzer with custom recognizers (exclude URL recognizer for image references)
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()
        self.language = language
        self.anonymize = anonymize
        
        # Image file extensions to exclude from URL detection
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg', '.ico', '.jfif']
        
        # Common safe domains to whitelist
        self.safe_domains = ['example.com', 'localhost', '127.0.0.1', 'github.com', 'stackoverflow.com', 'wikipedia.org']

    def scan(self, text: str) -> ScanResult:
        """
        Run Presidio detection and optional anonymization.
        Returns flagged=True if PII entities detected.
        Filters out image URLs and common false positives to reduce false positives.
        """
        try:
            results = self.analyzer.analyze(text=text, language=self.language)

            if results:
                # Filter out image URLs, safe domains, and common false positives
                filtered_results = []
                for result in results:
                    # Extract the detected text
                    detected_text = text[result.start:result.end].lower().strip()
                    
                    # Check if this is a URL entity
                    if result.entity_type == "URL":
                        # Check if it's an image URL
                        is_image_url = any(ext in detected_text for ext in self.image_extensions)
                        
                        # Check if it's a safe domain
                        is_safe_domain = any(domain in detected_text for domain in self.safe_domains)
                        
                        # Only include non-image URLs and non-safe domains
                        if not is_image_url and not is_safe_domain:
                            filtered_results.append(result)
                    elif result.entity_type == "DATE_TIME":
                        # Filter out common date/time words that are not actually PII
                        common_time_words = [
                            'today', 'yesterday', 'tomorrow', 'now', 'later', 'earlier',
                            'morning', 'afternoon', 'evening', 'night', 'tonight',
                            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                            'january', 'february', 'march', 'april', 'may', 'june',
                            'july', 'august', 'september', 'october', 'november', 'december'
                        ]
                        
                        # Only flag if it's not a common word and has high confidence
                        if detected_text not in common_time_words and result.score > 0.9:
                            filtered_results.append(result)
                    elif result.entity_type == "PERSON":
                        # Filter out common names that are not actually PII
                        common_names = [
                            'john', 'jane', 'smith', 'doe', 'admin', 'user', 'test',
                            'hello', 'hi', 'thanks', 'please', 'sorry', 'ok', 'yes', 'no'
                        ]
                        
                        # Only flag if it's not a common word and has high confidence
                        if detected_text not in common_names and result.score > 0.9:
                            filtered_results.append(result)
                    else:
                        # For other entity types, only include if high confidence
                        if result.score > 0.9:
                            filtered_results.append(result)
                
                # Only flag if we have non-image URL results
                if filtered_results:
                    anonymized_text = None
                    if self.anonymize:
                        anonymized = self.anonymizer.anonymize(
                            text=text,
                            analyzer_results=filtered_results
                        )
                        anonymized_text = anonymized.text

                    return ScanResult(
                        name="presidio",
                        flagged=True,
                        score=1.0,
                        reasons=[r.to_dict() for r in filtered_results],
                        extra={"anonymized": anonymized_text}
                    )

            # No PII detected (or only image URLs filtered out)
            return ScanResult("presidio", flagged=False, score=0.0)

        except Exception as e:
            return ScanResult("presidio", flagged=False, reasons=[str(e)])
