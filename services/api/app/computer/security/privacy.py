"""Privacy filter redacting passwords and sensitive data from accessibility trees (Stage 17)."""

import re
from typing import Any

from app.computer.contracts import UITreeNode

# Regex patterns for sensitive data
PASSWORD_NAME_PATTERNS = re.compile(r"(password|pwd|secret|passcode|token|pin)", re.IGNORECASE)
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class PrivacyFilter:
    """Sanitizes sensitive values in UI Automation trees and action parameters."""

    @classmethod
    def sanitize_tree_node(cls, node: UITreeNode) -> UITreeNode:
        """Recursively redacts password fields and sensitive values in an accessibility tree."""
        el = node.element

        is_sensitive = False
        if el.control_type == "Edit" and el.name and PASSWORD_NAME_PATTERNS.search(el.name):
            is_sensitive = True
        elif el.automation_id and PASSWORD_NAME_PATTERNS.search(el.automation_id):
            is_sensitive = True

        if is_sensitive:
            el.value = "[REDACTED_PASSWORD]"

        if el.value:
            # Mask potential credit card numbers or SSNs
            if CREDIT_CARD_PATTERN.search(el.value):
                el.value = "[REDACTED_PAYMENT_CARD]"
            elif SSN_PATTERN.search(el.value):
                el.value = "[REDACTED_SSN]"

        sanitized_children = [cls.sanitize_tree_node(child) for child in node.children]
        return UITreeNode(element=el, children=sanitized_children)

    @classmethod
    def sanitize_log_text(cls, text: str) -> str:
        """Sanitizes text before logging to disk or event bus."""
        cleaned = CREDIT_CARD_PATTERN.sub("[REDACTED_CARD]", text)
        cleaned = SSN_PATTERN.sub("[REDACTED_SSN]", cleaned)
        return cleaned


privacy_filter = PrivacyFilter()
