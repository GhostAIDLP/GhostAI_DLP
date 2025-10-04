import pytest
from normalize import normalize
from policy import apply_policies

# fake ScanResult class for testing
class ScanResult:
    def __init__(self, name, flagged, score, reasons, extra=None):
        self.name = name
        self.flagged = flagged
        self.score = score
        self.reasons = reasons
        self.extra = extra or {}

def test_normalize_basic():
    results = [
        ScanResult("gitleaks", True, 5.0, ["High entropy string"], {"file_path": "src/app.py"})
    ]
    normalized = normalize(results)
    assert len(normalized) == 1
    f = normalized[0]
    assert f["detector"] == "gitleaks"
    assert f["flagged"] is True
    assert f["score"] == 5.0
    assert "file_path" in f["extra"]

def test_policy_after_normalize():
    results = [
        ScanResult("gitleaks", True, 5.0, ["High entropy string"], {"file_path": "src/app.py"})
    ]
    normalized = normalize(results)
    rules = [
        {"id": "block_entropy", "if": 'detector=="gitleaks" and score>4.5', "action": "block"}
    ]
    decisions = apply_policies(normalized, rules)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "block"

def test_normalize_multiple():
    results = [
        ScanResult("gitleaks", True, 5.0, ["Key found"], {"file_path": "src/app.py"}),
        ScanResult("trufflehog", False, 1.0, [], {"file_path": "docs/readme.md"})
    ]
    normalized = normalize(results)
    assert len(normalized) == 2
    assert normalized[0]["detector"] == "gitleaks"
    assert normalized[1]["detector"] == "trufflehog"
