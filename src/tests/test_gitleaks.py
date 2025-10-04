import pytest
import json

from scanners.base import ScanResult
from types import SimpleNamespace


gitleaks_mod = pytest.importorskip("scanners.gitleaks_scanner", reason="GitleaksScanner not implemented/available")
GitleaksScanner = gitleaks_mod.GitleaksScanner

@pytest.fixture
def scanner():
    return GitleaksScanner()

def test_gitleaks_basic_positive(scanner, monkeypatch):
    fake_output = [{"rule": "generic_api_key", "file": "src/app.py", "lineNumber": 10,
                    "match": "OPENAI_API_KEY=sk-test-123", "entropy": 4.8}]
    fake_result = SimpleNamespace(stdout=json.dumps(fake_output).encode(), returncode=0)

    # Patch the class method so it's bound (self is passed)
    monkeypatch.setattr(GitleaksScanner, "_run_gitleaks", lambda self, text: fake_result)

    res = scanner.scan("ignored_text")
    assert res.flagged is True

def test_gitleaks_negative(scanner, monkeypatch):
    monkeypatch.setattr(scanner, "_run_gitleaks", lambda: [])
    res = scanner.scan("nothing")
    assert res.flagged is False
