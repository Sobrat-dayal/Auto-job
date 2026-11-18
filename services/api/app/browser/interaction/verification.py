"""Post-action verification for browser operations."""

import logging
from typing import Any
from playwright.async_api import Page

from app.browser.contracts import BrowserActionType
from app.browser.interaction.locators import LocatorResolver

logger = logging.getLogger(__name__)


class ActionVerifier:
    """Verifies that browser actions produced their intended effects."""

    @classmethod
    async def verify(
        cls,
        page: Page,
        action_type: BrowserActionType,
        target_locator: str | None,
        parameters: dict[str, Any],
        pre_url: str | None = None,
    ) -> dict[str, Any]:
        """Runs verification checks based on action type."""
        verification = {
            "verified": True,
            "action_type": action_type.value,
            "notes": [],
        }

        try:
            if action_type == BrowserActionType.NAVIGATE:
                expected_url = parameters.get("url", "")
                cur_url = page.url
                if expected_url and expected_url not in cur_url and cur_url not in expected_url:
                    verification["verified"] = False
                    verification["notes"].append(f"URL mismatch: expected '{expected_url}', currently '{cur_url}'")
                else:
                    verification["notes"].append(f"Successfully arrived at {cur_url}")

            elif action_type == BrowserActionType.FILL:
                if target_locator:
                    loc = LocatorResolver.resolve(page, target_locator)
                    val = await loc.input_value()
                    expected_val = str(parameters.get("value", ""))
                    if val != expected_val:
                        verification["verified"] = False
                        verification["notes"].append(f"Input value mismatch: expected '{expected_val}', found '{val}'")
                    else:
                        verification["notes"].append("Input value verified.")

            elif action_type == BrowserActionType.CHECK:
                if target_locator:
                    loc = LocatorResolver.resolve(page, target_locator)
                    is_checked = await loc.is_checked()
                    expected_checked = parameters.get("checked", True)
                    if is_checked != expected_checked:
                        verification["verified"] = False
                        verification["notes"].append(f"Checkbox state mismatch: expected {expected_checked}, got {is_checked}")
                    else:
                        verification["notes"].append("Checkbox state verified.")

            elif action_type == BrowserActionType.CLICK:
                cur_url = page.url
                if pre_url and cur_url != pre_url:
                    verification["notes"].append(f"Click triggered navigation to {cur_url}")
                else:
                    verification["notes"].append("Click executed on target element.")

        except Exception as exc:
            verification["verified"] = False
            verification["notes"].append(f"Verification exception: {exc}")

        return verification
