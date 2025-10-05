# src/scanners/prompt_guard2_scanner.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .base import BaseScanner, ScanResult

class PromptGuard2Scanner(BaseScanner):
    def __init__(
        self,
        model_name: str = "meta-llama/PromptGuard-2",
        threshold: float = 0.8,
        tokenizer=None,
        model=None,
    ):
        self.model_name = model_name
        self.threshold = threshold
        self.tokenizer = tokenizer or AutoTokenizer.from_pretrained(model_name)
        self.model = model or AutoModelForSequenceClassification.from_pretrained(model_name)

        # Optional: robust malicious index from config
        cfg = getattr(self.model, "config", None)
        id2label = getattr(cfg, "id2label", None)
        self._mal_idx = 1
        if isinstance(id2label, dict):
            for k, v in id2label.items():
                if str(v).lower().startswith("mal"):
                    self._mal_idx = int(k)
                    break

    def scan(self, text: str) -> ScanResult:
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1).squeeze()

            malicious_score = float(scores[self._mal_idx].item())
            flagged = malicious_score >= self.threshold
            return ScanResult(
                name="promptguard2",
                flagged=flagged,
                score=malicious_score,
                reasons=[{"score": malicious_score, "threshold": self.threshold}],
            )
        except Exception as e:
            return ScanResult("promptguard2", flagged=False, reasons=[str(e)])
