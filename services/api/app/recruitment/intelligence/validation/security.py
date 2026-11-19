"""Security validation and prompt injection defense for untrusted job postings."""

import re

# Prompt injection patterns commonly embedded in adversarial text
INJECTION_PATTERNS = [
    re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior)\s+instructions\b", re.IGNORECASE),
    re.compile(r"\bsystem\s+override\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+now\s+(?:an?\s+)?(?:unrestricted|admin|god)\b", re.IGNORECASE),
    re.compile(r"\bmark\s+(?:this\s+)?applicant\s+as\s+(?:hired|approved|100%|matched)\b", re.IGNORECASE),
    re.compile(r"<\s*script\b[^>]*>", re.IGNORECASE),
    re.compile(r"javascript:\s*", re.IGNORECASE),
]


def sanitize_untrusted_job_text(text: str) -> str:
    """Defuse potential prompt injections in job descriptions before analysis."""
    if not text:
        return ""

    sanitized = text
    for pattern in INJECTION_PATTERNS:
        sanitized = pattern.sub("[POTENTIAL_INJECTION_DEFUSED]", sanitized)

    return sanitized


def detect_adversarial_content(text: str) -> list[str]:
    """Detect presence of adversarial phrases in job posting text."""
    warnings: list[str] = []
    if not text:
        return warnings

    for pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            warnings.append(f"Potential prompt injection detected: '{match.group(0)}'")

    return warnings
