# src/scanners/regex_secrets_scanner.py
import re
from .base import BaseScanner, ScanResult

class RegexSecretsScanner(BaseScanner):
    def __init__(self):
        # Define common secret patterns
        self.patterns = {
            'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
            'aws_secret_key': re.compile(r'[A-Za-z0-9/+=]{40}', re.IGNORECASE),
            'api_key': re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?'),
            'bearer_token': re.compile(r'bearer\s+[A-Za-z0-9_\-\.]{20,}', re.IGNORECASE),
            'jwt_token': re.compile(r'eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+'),
            'private_key': re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'),
            'password': re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([A-Za-z0-9_\-@#$%^&*()!]{8,})["\']?'),
            'secret': re.compile(r'(?i)(secret|secretkey|secret_key)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{16,})["\']?'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'ssn_no_dashes': re.compile(r'\b\d{9}\b'),
            'jailbreak_prompt': re.compile(r'(?i)(ignore\s+all\s+previous\s+instructions|forget\s+everything|you\s+are\s+now|act\s+as\s+if|pretend\s+to\s+be)', re.IGNORECASE),
        }

    def scan(self, text: str) -> ScanResult:
        """
        Scan text for common secret patterns using regex.
        """
        findings = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        # For patterns with groups, use the second group (the actual secret)
                        secret_value = match[1] if len(match) > 1 else match[0]
                    else:
                        secret_value = match
                    
                    findings.append({
                        'pattern': pattern_name,
                        'value': secret_value[:20] + '...' if len(secret_value) > 20 else secret_value,
                        'position': text.find(secret_value)
                    })

        return ScanResult(
            name="regex_secrets",
            flagged=bool(findings),
            score=1.0 if findings else 0.0,
            reasons=findings
        )
