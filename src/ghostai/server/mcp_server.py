from mcp.server import Server
from policies.engine import apply_policies
from src.normalize import normalize

server = Server("ghostai")

# --- Tools ---

def tool(name):
    def decorator(func):
        """
        Decorator to register a tool with the server under a given name.

        The decorated function will be set as an attribute of the server object.

        :param func: The function to be decorated
        :return: The decorated function
        """
        setattr(server, name, func)
        return func
    return decorator

@tool("normalize")
def normalize_tool(findings: list) -> list:
    """
    Normalize raw scanner findings into GhostAI schema.
    """
    return normalize(findings)

@tool("decide")
def decide_tool(findings: list, rules: list) -> list:
    """
    Apply policies to normalized findings.
    """
    return apply_policies(findings, rules)

@tool("run")
def run_tool(rules: list) -> list:
    """
    Run scanners, normalize, and apply policies (one-shot).
    Stubbed for now.
    """
    # TODO: call your scanner wrappers
    findings = [{"detector": "gitleaks", "score": 5.0, "file_path": "src/app.py"}]
    normalized = normalize(findings)
    return apply_policies(normalized, rules)

@tool("get_rules")
def get_rules_tool() -> dict:
    """
    Return current policy rules (YAML/JSON).
    Stub until connected to your rules storage.
    """
    return {"rules": []}

@tool("set_rules")
def set_rules_tool(rules: list) -> dict:
    """
    Update policy rules (YAML/JSON).
    Stub until connected to your rules storage.
    """
    return {"status": "ok", "rules": rules}
