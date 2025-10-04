import pytest
from scanners.base import ScanResult

# Import (skip if class/file not present yet)
presidio_mod = pytest.importorskip("scanners.presidio_scanner", reason="PresidioScanner not implemented/available")
PresidioScanner = presidio_mod.PresidioScanner

class _FakeAnalyzerResult:
    # Mimics Presidio Result object enough for .to_dict() usage
    def __init__(self, entity_type="US_SSN", score=0.9, start=11, end=22):
        self.entity_type = entity_type
        self.score = score
        self.start = start
        self.end = end
    def to_dict(self):
        return {
            "entity_type": self.entity_type,
            "score": self.score,
            "start": self.start,
            "end": self.end
        }

class _FakeAnonymizeReturn:
    def __init__(self, text):
        self.text = text

@pytest.fixture
def scanner():
    return PresidioScanner(language="en", anonymize=True)

def test_presidio_flags_when_entities_found(monkeypatch, scanner):
    # Fake analyzer returns one SSN hit
    monkeypatch.setattr(scanner.analyzer, "analyze", lambda text, language: [_FakeAnalyzerResult()])
    # Fake anonymizer returns masked text
    monkeypatch.setattr(scanner.anonymizer, "anonymize", lambda text, analyzer_results: _FakeAnonymizeReturn("XXX-XX-6789"))

    res = scanner.scan("My SSN is 123-45-6789")
    assert isinstance(res, ScanResult)
    assert res.name == "presidio"
    assert res.flagged is True
    assert res.score == 1.0
    assert isinstance(res.reasons, list) and len(res.reasons) == 1
    assert res.extra.get("anonymized") == "XXX-XX-6789"

def test_presidio_no_hits_returns_not_flagged(monkeypatch, scanner):
    monkeypatch.setattr(scanner.analyzer, "analyze", lambda text, language: [])
    res = scanner.scan("Hello world.")
    assert res.flagged is False
    assert res.score == 0.0
    assert res.reasons == []
    assert res.extra == {}

def test_presidio_handles_exception(monkeypatch, scanner):
    def boom(*args, **kwargs):
        raise RuntimeError("analyzer exploded")
    monkeypatch.setattr(scanner.analyzer, "analyze", boom)

    res = scanner.scan("anything")
    assert res.flagged is False
    # error message captured in reasons
    assert any("exploded" in str(r) for r in res.reasons)
