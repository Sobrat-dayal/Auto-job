"""Secret Scanning & Redaction Engine for Repository Source Code (Stage 22)."""

from __future__ import annotations

import re

# Comprehensive high-precision patterns for tokens, keys, and credentials
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"),  # GitHub Tokens
    re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),  # AWS Access Key ID
    re.compile(r"(?i)(api[_-]?key|secret|token|password|auth|bearer)\s*[:=]\s*['\"][A-Za-z0-9_.\-+/]{16,}['\"]"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),  # JWT Tokens
    re.compile(r"(postgres|mysql|mongodb|redis)://[a-zA-Z0-9_\-]+:[^@\s]+@[a-zA-Z0-9.\-_]+"),  # DB connection URLs
]


class SecretRedactor:
    """Scans and redacts credentials, private keys, and tokens from source code snippets."""

    @classmethod
    def contains_secret(cls, text: str) -> bool:
        """Returns True if any sensitive credential pattern is detected."""
        return any(p.search(text) is not None for p in SECRET_PATTERNS)

    @classmethod
    def redact(cls, text: str) -> tuple[str, bool]:
        """Redacts sensitive values and returns (sanitized_text, has_redactions)."""
        has_redacted = False
        result = text
        for pattern in SECRET_PATTERNS:
            if pattern.search(result):
                has_redacted = True
                result = pattern.sub("[REDACTED_SECRET]", result)
        return result, has_redacted
