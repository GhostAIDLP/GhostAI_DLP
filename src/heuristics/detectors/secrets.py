from . import Detector
from typing import Tuple, List

class SecretsDetector(Detector):
    """High-precision secret signatures (PEM, AKIA, ghp_, sk_live_)."""
    name = "secrets"