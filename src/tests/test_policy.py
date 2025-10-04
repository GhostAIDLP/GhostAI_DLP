import pytest
from policy import apply_policies  # adjust import

def test_block_high_entropy():
    findings = [
        {"detector": "gitleaks", "score": 5.0, "file_path": "src/app.py"}
    ]
    rules = [
        {"id": "block_entropy", "if": 'detector=="gitleaks" and score>4.5', "action": "block"}
    ]
    decisions = apply_policies(findings, rules)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "block"

def test_warn_in_tests_folder():
    findings = [
        {"detector": "gitleaks", "score": 2.0, "file_path": "tests/test.py"}
    ]
    rules = [
        {"id": "warn_tests", "if": 'file_path.startswith("tests/")', "action": "warn"}
    ]
    decisions = apply_policies(findings, rules)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "warn"

def test_no_match():
    findings = [
        {"detector": "trufflehog", "score": 1.0, "file_path": "docs/readme.md"}
    ]
    rules = [
        {"id": "block_entropy", "if": 'detector=="gitleaks" and score>4.5', "action": "block"}
    ]
    decisions = apply_policies(findings, rules)
    assert decisions == []
