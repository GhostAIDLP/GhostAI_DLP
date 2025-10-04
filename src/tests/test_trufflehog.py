# tests/test_trufflehog.py
import json
import types
import pytest
from scanners.base import ScanResult

truff_mod = pytest.importorskip(
    "scanners.trufflehog_scanner", reason="TrufflehogScanner not available"
)
TrufflehogScanner = truff_mod.TrufflehogScanner

@pytest.fixture
def scanner():
    return TrufflehogScanner()


def _fake_cp(stdout_text: str, returncode: int = 0, stderr_text: str = ""):
    """Mimic subprocess.CompletedProcess shape enough for the scanner."""
    return types.SimpleNamespace(
        stdout=stdout_text.encode("utf-8"),
        stderr=stderr_text.encode("utf-8"),
        returncode=returncode,
    )


def test_trufflehog_positive_multiple_lines(scanner, monkeypatch):
    line1 = {"DetectorName": "HighEntropy", "File": "a.py", "Line": 10, "Raw": "AAA", "Entropy": 5.0}
    line2 = {"DetectorName": "AWS", "File": "b.ts", "Line": 7, "Raw": "AKIA...", "Entropy": 4.6}
    stdout = json.dumps(line1) + "\n" + json.dumps(line2) + "\n"

    monkeypatch.setattr(
        TrufflehogScanner, "_run_trufflehog", lambda self, text: _fake_cp(stdout)
    )

    res = scanner.scan("dummy")
    assert isinstance(res, ScanResult)
    assert res.name == "trufflehog"
    assert res.flagged is True
    assert res.score == 1.0
    assert isinstance(res.reasons, list) and len(res.reasons) == 2
    assert res.reasons[0]["DetectorName"] == "HighEntropy"


def test_trufflehog_malformed_line_falls_back_to_raw(scanner, monkeypatch):
    bad = '{"DetectorName": "HighEntropy"'  # missing closing brace
    good = {"DetectorName": "GCP", "File": "c.js", "Line": 3, "Raw": "ya29...", "Entropy": 4.9}
    stdout = bad + "\n" + json.dumps(good) + "\n"

    monkeypatch.setattr(
        TrufflehogScanner, "_run_trufflehog", lambda self, text: _fake_cp(stdout)
    )

    res = scanner.scan("dummy")
    assert res.flagged is True
    assert res.score == 1.0
    assert isinstance(res.reasons[0], dict) and "raw" in res.reasons[0]
    assert res.reasons[1]["DetectorName"] == "GCP"


def test_trufflehog_ignores_blank_lines(scanner, monkeypatch):
    line = {"DetectorName": "Entropy", "File": "x", "Line": 1, "Raw": "ZZZ", "Entropy": 5.1}
    stdout = "\n  \n" + json.dumps(line) + "\n\n"

    monkeypatch.setattr(
        TrufflehogScanner, "_run_trufflehog", lambda self, text: _fake_cp(stdout)
    )

    res = scanner.scan("dummy")
    assert res.flagged is True
    assert len(res.reasons) == 1


def test_trufflehog_negative_sets_score_and_reasons(scanner, monkeypatch):
    monkeypatch.setattr(
        TrufflehogScanner, "_run_trufflehog", lambda self, text: _fake_cp("")
    )

    res = scanner.scan("nothing")
    assert res.flagged is False
    assert res.score == 0.0
    assert res.reasons == []


def test_trufflehog_nonzero_returncode_with_output_is_still_flagged(scanner, monkeypatch):
    # Current behavior: returncode is ignored; findings still count if stdout has lines
    line = {"DetectorName": "Entropy", "File": "a", "Line": 1, "Raw": "AAA", "Entropy": 5.0}
    stdout = json.dumps(line) + "\n"

    monkeypatch.setattr(
        TrufflehogScanner, "_run_trufflehog",
        lambda self, text: _fake_cp(stdout, returncode=2, stderr_text="warn"),
    )

    res = scanner.scan("dummy")
    assert res.flagged is True
    assert res.score == 1.0
    assert res.reasons and res.reasons[0]["DetectorName"] == "Entropy"


def test_trufflehog_exception_path(scanner, monkeypatch):
    def boom(self, text):
        raise OSError("trufflehog not found")

    monkeypatch.setattr(TrufflehogScanner, "_run_trufflehog", boom)

    res = scanner.scan("dummy")
    assert res.flagged is False
    assert any("not found" in str(x) for x in res.reasons)
