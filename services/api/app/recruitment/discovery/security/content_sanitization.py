"""Content sanitization and prompt injection containment for job descriptions (Stage 26)."""

import html
import re


DANGEROUS_HTML_TAGS = re.compile(
    r"<\s*(script|style|iframe|object|embed|applet|form|input|button|meta|link)[^>]*>.*?</\s*\1\s*>",
    re.IGNORECASE | re.DOTALL,
)

SELF_CLOSING_DANGEROUS_TAGS = re.compile(
    r"<\s*(script|style|iframe|object|embed|applet|form|input|button|meta|link)[^>]*/*>",
    re.IGNORECASE,
)

EVENT_HANDLER_ATTRS = re.compile(
    r'\s+on[a-zA-Z]+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)',
    re.IGNORECASE,
)

JAVASCRIPT_URLS = re.compile(
    r'(href|src)\s*=\s*(?:"javascript:[^"]*"|\'javascript:[^\']*\'|javascript:[^\s>]+)',
    re.IGNORECASE,
)

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|existing|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
    re.compile(r"export\s+applicant\s+profile", re.IGNORECASE),
    re.compile(r"bypass\s+recruitment\s+policy", re.IGNORECASE),
    re.compile(r"submit\s+application\s+immediately\s+without\s+review", re.IGNORECASE),
]


def sanitize_html(html_content: str) -> str:
    """Sanitize raw HTML by stripping dangerous script/iframe tags and event handlers."""
    if not html_content or not isinstance(html_content, str):
        return ""

    sanitized = DANGEROUS_HTML_TAGS.sub("", html_content)
    sanitized = SELF_CLOSING_DANGEROUS_TAGS.sub("", sanitized)
    sanitized = EVENT_HANDLER_ATTRS.sub("", sanitized)
    sanitized = JAVASCRIPT_URLS.sub(r'\1="#"', sanitized)

    return sanitized.strip()


def check_for_prompt_injection(text: str) -> tuple[bool, list[str]]:
    """Detect if untrusted job description contains prompt injection keywords."""
    if not text:
        return False, []

    detected = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            detected.append(pattern.pattern)

    return len(detected) > 0, detected


def neutralize_prompt_injection(text: str) -> str:
    """Wrap untrusted job text in safety boundaries to prevent LLM prompt escaping."""
    if not text:
        return ""

    # Disarm known injection patterns by neutralizing raw instructions
    safe_text = text
    for pattern in INJECTION_PATTERNS:
        safe_text = pattern.sub(lambda m: "[POTENTIAL_INJECTION_DEFUSED]", safe_text)

    return safe_text


# Aliases
sanitize_html_content = sanitize_html
disarm_prompt_injection = neutralize_prompt_injection
