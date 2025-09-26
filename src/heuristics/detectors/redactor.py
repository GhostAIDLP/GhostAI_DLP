from heuristics.types.redactor_types import RedactedFinding, RedactionRule, RedactionDefaults

class Redactor:
    def __init__(self, config):
        self.rules: RedactionRule = config["rules"]
        self.defaults: RedactionDefaults = config["defaults"]

    def redact(self, finding: RedactedFinding) -> str:
        rule = (
            self.rules.get(finding.id)
            or self.defaults["provider"].get(finding.provider)
            or self.defaults["category"].get(finding.category)
            or self.defaults["global"]
        )

        if rule.get("passthrough"):
            return finding.match

        return self._apply_mask(finding.match, rule)

    def _apply_mask(self, text: str, rule):
        prefix, suffix, mask = rule["prefix"], rule["suffix"], rule["mask"]
        if len(text) <= prefix + suffix:
            return mask
        return text[:prefix] + mask + text[-suffix:]
