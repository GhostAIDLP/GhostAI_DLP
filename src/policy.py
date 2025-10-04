from typing import List, Dict, Any

def apply_policies(findings: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply rules-as-code to findings. Each rule has `if` condition and `action`.
    """
    decisions = []
    for f in findings:
        for rule in rules:
            if eval(rule["if"], {}, f):   # replace with safe condition parser
                decisions.append({
                    "finding": f,
                    "rule_id": rule["id"],
                    "action": rule["action"]
                })
    return decisions
