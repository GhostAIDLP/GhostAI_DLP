import pytest
from policies.engine import apply_policies

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

def test_no_match():
    findings = [
        {"detector": "trufflehog", "score": 1.0, "file_path": "docs/readme.md"}
    ]
    rules = [
        {"id": "block_entropy", "if": 'detector=="gitleaks" and score>4.5', "action": "block"}
    ]
    decisions = apply_policies(findings, rules)
    assert decisions == []

def test_warn_in_tests_folder():
    findings = [
        {"detector": "gitleaks", "score": 2.0, "file_path": "tests/test.py"}
    ]
    rules = [
        {"id": "warn_tests", "if": 'LIKE(file_path, "tests/**")', "action": "warn"}
    ]
    decisions = apply_policies(findings, rules)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "warn"


def test_like_function():
    findings = [{"detector": "gitleaks", "score": 3.0, "file_path": "src/app.py"}]
    rules = [
        {"id": "like_rule", "if": 'LIKE(file_path, "src/*.py")', "action": "warn"}
    ]
    decisions = apply_policies(findings, rules)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "warn"


def test_malicious_code_is_blocked():
    findings = [{"detector": "gitleaks", "score": 3.0, "file_path": "src/app.py"}]
    rules = [
        {
            "id": "evil",
            "if": '__import__("os").system("echo hacked")',
            "action": "block",
        }
    ]
    decisions = apply_policies(findings, rules)
    # invalid code should be ignored, not executed
    assert decisions[0]["action"] == "error"
