"""Logical requirement relationship parser and negation analyzer."""

import re

from app.recruitment.intelligence.contracts import LogicalOperator

# Patterns that indicate negation of a requirement
NEGATION_PATTERNS = [
    re.compile(r"\bnot\s+(?:required|mandatory|necessary|needed|expected)\b", re.IGNORECASE),
    re.compile(r"\bno\s+(?:prior|previous)?\s*(?:experience|degree|certification)\s+(?:is\s+)?required\b", re.IGNORECASE),
    re.compile(r"\b(?:without|neither|nor)\b", re.IGNORECASE),
    re.compile(r"\b(?:sponsorship\s+(?:is\s+)?unavailable|no\s+visa\s+sponsorship)\b", re.IGNORECASE),
    re.compile(r"\bnot\s+eligible\b", re.IGNORECASE),
    re.compile(r"\b(?:cannot|will\s+not)\s+be\s+considered\b", re.IGNORECASE),
]

AT_LEAST_N_PATTERN = re.compile(
    r"\b(?:any|at\s+least|minimum\s+of|one\s+or\s+more\s+of)\s*(\d+|one|two|three|four|five)?\s*(?:of\s+the\s+following)?\b",
    re.IGNORECASE,
)

WORD_TO_NUM = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def is_negated_phrase(text: str) -> bool:
    """Check if the text segment contains explicit negative phrasing for a requirement."""
    for pattern in NEGATION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def is_skill_negated(text: str, skill_name: str) -> bool:
    """Determine if a specific skill mention is scoped inside a negation phrase."""
    # Example: "AWS experience not required" or "No prior AWS experience needed"
    escaped_skill = re.escape(skill_name)
    patterns = [
        re.compile(rf"\b{escaped_skill}\b[^\.\,\;]*?\bnot\s+(?:required|needed|mandatory)\b", re.IGNORECASE),
        re.compile(rf"\bnot\s+(?:required|needed|mandatory)\b[^\.\,\;]*?\b{escaped_skill}\b", re.IGNORECASE),
        re.compile(rf"\bno\b[^\.\,\;]*?\b{escaped_skill}\b[^\.\,\;]*?\b(?:required|needed)\b", re.IGNORECASE),
        re.compile(rf"\boptional\b[^\.\,\;]*?\b{escaped_skill}\b", re.IGNORECASE),
    ]
    for p in patterns:
        if p.search(text):
            return True
    return False


def detect_logical_operator(text: str) -> tuple[LogicalOperator, int | None]:
    """Detect logical operator and optional min_count for a compound requirement string."""
    # Check AtLeastN
    at_least_match = AT_LEAST_N_PATTERN.search(text)
    if at_least_match:
        raw_num = at_least_match.group(1)
        if raw_num:
            raw_lower = raw_num.lower()
            num = int(raw_num) if raw_num.isdigit() else WORD_TO_NUM.get(raw_lower, 1)
            return LogicalOperator.AT_LEAST_N, num
        return LogicalOperator.AT_LEAST_N, 1

    # Check equivalent alternative
    if re.search(r"\bor\s+equivalent\s+(?:practical|work)?\s*experience\b", text, re.IGNORECASE):
        return LogicalOperator.EQUIVALENT_ALTERNATIVE, None

    # Check simple OR
    if re.search(r"\b(?:or|either)\b", text, re.IGNORECASE):
        return LogicalOperator.OR, None

    # Check AND
    if re.search(r"\b(?:and|both|as\s+well\s+as)\b", text, re.IGNORECASE):
        return LogicalOperator.AND, None

    return LogicalOperator.AND, None
