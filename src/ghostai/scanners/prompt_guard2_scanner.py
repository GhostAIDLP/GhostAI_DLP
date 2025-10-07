import os
from huggingface_hub import InferenceClient
from .base import BaseScanner, ScanResult


class PromptGuard2Scanner(BaseScanner):
    """
    Cloud-based prompt injection detector using HuggingFace's hosted Zephyr-7B model.
    Responds instantly, no local weights required.
    """

    def __init__(
        self,
        model_name: str = "HuggingFaceH4/zephyr-7b-beta",
        threshold: float = 0.5,
        token: str | None = None,
    ):
        # read HF token from env or argument
        self.model_name = model_name
        self.threshold = threshold
        self.token = token or os.getenv("HF_TOKEN")
        self.client = InferenceClient(model_name, token=self.token)

    def scan(self, text: str) -> ScanResult:
        """
        Send text to the hosted Zephyr chat-completion endpoint.
        Returns SAFE or INJECTION with a pseudo-score.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a security classifier. Respond only with SAFE or INJECTION.",
                },
                {"role": "user", "content": f"Text: {text}\nLabel:"},
            ]

            response = self.client.chat_completion(messages=messages, max_tokens=5)
            reply = response.choices[0].message["content"].strip().upper()

            flagged = "INJECTION" in reply
            score = 1.0 if flagged else 0.0

            return ScanResult(
                name="promptguard2-zephyr",
                flagged=flagged,
                score=score,
                reasons=[{"raw": reply, "threshold": self.threshold}],
            )

        except Exception as e:
            # graceful fallback
            return ScanResult(
                name="promptguard2-zephyr",
                flagged=False,
                score=0.0,
                reasons=[{"error": str(e)}],
            )
