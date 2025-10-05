from typing import List, Dict, Any
import ast, operator as op, fnmatch

# Allowed comparison + boolean ops
ALLOWED_OPS = {
    ast.Eq:  op.eq,
    ast.NotEq: op.ne,
    ast.Gt:  op.gt,
    ast.GtE: op.ge,
    ast.Lt:  op.lt,
    ast.LtE: op.le,
    ast.In:  lambda a, b: a in b,
    ast.And: lambda a, b: a and b,
    ast.Or:  lambda a, b: a or b,
}

# LIKE helper
def _like(text: str, pattern: str) -> bool:
    return fnmatch.fnmatch(text, pattern)

SAFE_FUNCS = {"LIKE": _like, "like": _like}

# Core evaluator
def _eval(node, ctx):
    if isinstance(node, ast.BoolOp):
        vals = [_eval(v, ctx) for v in node.values]
        res = vals[0]
        for v in vals[1:]:
            res = ALLOWED_OPS[type(node.op)](res, v)
        return res
    if isinstance(node, ast.Compare):
        left = _eval(node.left, ctx)
        for opnode, comp in zip(node.ops, node.comparators):
            right = _eval(comp, ctx)
            left = ALLOWED_OPS[type(opnode)](left, right)
        return left
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _eval(node.operand, ctx)
    if isinstance(node, ast.Call):
        func = _eval(node.func, ctx)
        args = [_eval(a, ctx) for a in node.args]
        return func(*args)
    if isinstance(node, ast.Name):
        if node.id in ctx: return ctx[node.id]
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Unknown name: {node.id}")
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_eval(e, ctx) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {_eval(k, ctx): _eval(v, ctx) for k, v in zip(node.keys, node.values)}
    raise ValueError(f"Unsupported expression: {type(node).__name__}")

def safe_eval(expr: str, context: dict) -> bool:
    tree = ast.parse(expr, mode="eval")
    return bool(_eval(tree.body, context))

# Policy engine
def apply_policies(findings: List[Dict[str, Any]], rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    decisions = []
    for f in findings:
        ctx = {**f, **f.get("extra", {})}
        for rule in rules:
            cond = rule.get("if", "False")
            try:
                if safe_eval(cond, ctx):
                    decisions.append({
                        "finding": f,
                        "rule_id": rule["id"],
                        "action": rule["action"],
                        "reason": rule.get("reason"),
                    })
            except Exception as e:
                decisions.append({
                    "finding": f,
                    "rule_id": rule.get("id", "invalid_rule"),
                    "action": "error",
                    "reason": f"Rule evaluation error: {e}",
                })
    return decisions
