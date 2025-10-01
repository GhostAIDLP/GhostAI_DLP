# src/scanners/promptguard_scanner.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .base import BaseScanner, ScanResult

class PromptGuard2Scanner(BaseScanner):
    def __init__(self, model_name: str = "meta-llama/PromptGuard-2", threshold: float = 0.8):
        self.model_name = model_name
        self.threshold = threshold
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def scan(self, text: str) -> ScanResult:
        """
        Run PromptGuard2 model against text.
        Returns flagged=True if malicious score exceeds threshold.
        """
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1).squeeze()

            malicious_score = scores[1].item()  # assume index 1 = malicious
            flagged = malicious_score >= self.threshold

            return ScanResult(
                name="promptguard2",
                flagged=flagged,
                score=malicious_score,
                reasons=[{"score": malicious_score, "threshold": self.threshold}]
            )

        except Exception as e:
            return ScanResult("promptguard2", flagged=False, reasons=[str(e)])
