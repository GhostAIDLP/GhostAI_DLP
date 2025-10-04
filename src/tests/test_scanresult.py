# tests/test_scanresult_all.py
import pytest
from scanners.base import ScanResult

# --- Your originals (kept) ---
def test_scanresult_basics():
    r = ScanResult(
        name="dummy",
        flagged=True,
        score=0.75,
        reasons=[{"type": "pii", "entity": "SSN"}],
        extra={"anonymized": "***-**-6789", "commit": "abc123"},
    )
    assert r.name == "dummy"
    assert r.flagged is True
    assert r.score == 0.75
    assert isinstance(r.reasons, list)
    assert r.extra.get("commit") == "abc123"

def test_scanresult_to_dict_flattens_extra():
    r = ScanResult(
        name="x",
        flagged=False,
        score=0.0,
        reasons=[],
        extra={"foo": "bar", "anonymized": "XXX"},
    )
    d = r.to_dict()
    # base fields present
    assert d["name"] == "x"
    assert d["flagged"] is False
    assert d["score"] == 0.0
    assert d["reasons"] == []
    # extra flattened
    assert d["foo"] == "bar"
    assert d["anonymized"] == "XXX"

def test_scanresult_defaults():
    r = ScanResult(name="n", flagged=False)
    assert r.score == 0.0
    assert r.reasons == []
    assert r.extra == {}
    d = r.to_dict()
    # no extra keys added when extra is empty
    assert set(d.keys()) == {"name", "flagged", "score", "reasons"}

# --- Extra hardening tests ---
def test_scanresult_none_coalescing():
    r = ScanResult(name="n", flagged=False, reasons=None, extra=None)
    assert r.reasons == []
    assert r.extra == {}

def test_scanresult_defaults_are_not_shared():
    r1 = ScanResult("a", False)
    r2 = ScanResult("b", False)
    r1.reasons.append({"k": 1})
    r1.extra["x"] = 42
    assert r2.reasons == []          # not shared
    assert r2.extra == {}            # not shared

def test_scanresult_to_dict_no_mutation():
    r = ScanResult("x", True, extra={"foo": "bar"})
    before_reasons = list(r.reasons)
    before_extra = dict(r.extra)
    _ = r.to_dict()
    assert r.reasons == before_reasons
    assert r.extra == before_extra

# Current behavior: extras can overwrite base keys when flattened.
def test_scanresult_to_dict_allows_extra_overwrite():
    r = ScanResult(
        name="base",
        flagged=False,
        score=0.3,
        reasons=[1],
        extra={"name": "override", "flagged": True, "score": 0.9, "reasons": ["x"], "k": "v"},
    )
    d = r.to_dict()
    assert d["name"] == "override"
    assert d["flagged"] is True
    assert d["score"] == 0.9
    assert d["reasons"] == ["x"]
    assert d["k"] == "v"

# If you later forbid collisions, replace the test above with this one and
# add a collision guard in ScanResult.to_dict().
# def test_scanresult_to_dict_forbids_extra_key_collision():
#     r = ScanResult(name="n", flagged=True, extra={"name": "bad"})
#     with pytest.raises(KeyError):
#         _ = r.to_dict()

def test_flagged_without_reasons_is_allowed_currently():
    r = ScanResult("x", True)  # empty reasons by default
    assert r.flagged is True
    assert r.reasons == []
    # If you want to enforce reasons when flagged, change to:
    # assert r.reasons, "flagged results must include at least one reason"
