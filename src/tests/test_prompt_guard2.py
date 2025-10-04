# tests/test_prompt_guard2.py
import types
import pytest

# Make sure src/ is on PYTHONPATH (pytest.ini: pythonpath = src)
pg_mod = pytest.importorskip(
    "scanners.prompt_guard2_scanner",
    reason="PromptGuard2Scanner not available",
)
PromptGuard2Scanner = pg_mod.PromptGuard2Scanner  # local alias

# --- lightweight fakes ---
class _Tok:
    def __call__(self, text, **kw): 
        return {"input_ids": [1], "attention_mask": [1]}

class _Scores:
    def __init__(self, vec): self._vec = vec
    def squeeze(self): return self
    def __getitem__(self, i): return types.SimpleNamespace(item=lambda: self._vec[i])

class _NoGrad:
    def __enter__(self): return None
    def __exit__(self, *a): return False

class _TorchFake:
    def __init__(self, scores): self._scores = scores  # e.g., [benign_prob, malicious_prob]
    def softmax(self, logits, dim=1): return _Scores(self._scores)
    def no_grad(self): return _NoGrad()

class _Model:
    def __init__(self, id2label): self.config = types.SimpleNamespace(id2label=id2label)
    def __call__(self, **inp): return types.SimpleNamespace(logits=None)

def test_respects_id2label_and_threshold(monkeypatch):
    # id2label maps index 0->benign, 1->malicious
    model = _Model({0: "benign", 1: "malicious"})
    tok = _Tok()
    # malicious prob 0.85 -> should flag at threshold 0.8
    monkeypatch.setattr(pg_mod, "torch", _TorchFake([0.15, 0.85]))
    s = PromptGuard2Scanner(tokenizer=tok, model=model, threshold=0.8)
    res = s.scan("x")
    assert res.flagged is True and abs(res.score - 0.85) < 1e-9

def test_boundary_and_label_swap(monkeypatch):
    # labels swapped: 0->malicious, 1->benign; malicious prob at index 0
    model = _Model({1: "benign", 0: "malicious"})
    tok = _Tok()
    monkeypatch.setattr(pg_mod, "torch", _TorchFake([0.80, 0.20]))
    s = PromptGuard2Scanner(tokenizer=tok, model=model, threshold=0.8)
    res = s.scan("x")
    assert res.flagged is True and abs(res.score - 0.80) < 1e-9

def test_exception_bubbles_to_scanresult(monkeypatch):
    class _BadModel(_Model):
        def __call__(self, **inp): 
            raise RuntimeError("forward failed")

    tok = _Tok()
    bad = _BadModel({0: "benign", 1: "malicious"})
    monkeypatch.setattr(pg_mod, "torch", _TorchFake([0.10, 0.90]))
    s = PromptGuard2Scanner(tokenizer=tok, model=bad)
    res = s.scan("x")
    assert res.flagged is False
    assert any("forward failed" in str(r) for r in res.reasons)
