"""Smart locator resolution for robust browser element interaction."""

import logging
import re
from typing import Any
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class LocatorResolver:
    """Resolves semantic, accessibility, or CSS/XPath locators on a Playwright Page."""

    @classmethod
    def resolve(cls, page: Page, target: str) -> Locator:
        """Resolves a target string into a Playwright Locator instance."""
        target = target.strip()
        if not target:
            raise ValueError("Target locator string cannot be empty.")

        # Check for role syntax: e.g. role=button[name="Apply"] or role=link[name='Jobs']
        role_match = re.match(r"^role=([a-zA-Z0-9_\-]+)(?:\[name=['\"](.*)['\"]\])?$", target)
        if role_match:
            role_name = role_match.group(1)
            name_val = role_match.group(2)
            if name_val:
                return page.get_by_role(role_name, name=name_val)  # type: ignore
            return page.get_by_role(role_name)  # type: ignore

        # Check for placeholder syntax: placeholder="Search"
        placeholder_match = re.match(r"^placeholder=['\"](.*)['\"]$", target)
        if placeholder_match:
            return page.get_by_placeholder(placeholder_match.group(1))

        # Check for label syntax: label="Email Address"
        label_match = re.match(r"^label=['\"](.*)['\"]$", target)
        if label_match:
            return page.get_by_label(label_match.group(1))

        # Check for text syntax: text="Submit Application"
        text_match = re.match(r"^text=['\"](.*)['\"]$", target)
        if text_match:
            return page.get_by_text(text_match.group(1))

        # Check for test-id syntax: test-id="submit-btn" or data-testid="submit-btn"
        testid_match = re.match(r"^(?:test-id|data-testid)=['\"](.*)['\"]$", target)
        if testid_match:
            return page.get_by_test_id(testid_match.group(1))

        # Check for indexed DOM element syntax from DOMExtractor: e.g. [12] or element[12]
        indexed_match = re.match(r"^(?:element)?\[(\d+)\]$", target)
        if indexed_match:
            node_id = indexed_match.group(1)
            return page.locator(f"[data-autonom-id='{node_id}']")

        # Standard CSS or XPath locator
        return page.locator(target)
