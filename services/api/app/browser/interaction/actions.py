"""Typed action executor for Playwright browser operations."""

import logging
import time
from uuid import uuid4
from typing import Any
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from app.browser.contracts import (
    BrowserActionRequest,
    BrowserActionResponse,
    BrowserActionStatus,
    BrowserActionType,
)
from app.browser.interaction.locators import LocatorResolver

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes single or sequential browser actions on a Playwright Page."""

    @classmethod
    async def execute(
        cls,
        page: Page,
        session_id: str,
        tab_id: str,
        req: BrowserActionRequest,
    ) -> BrowserActionResponse:
        """Executes a requested browser action and returns the outcome."""
        action_id = str(uuid4())
        start_time = time.perf_counter()
        timeout = req.timeout_ms

        try:
            result_data: dict[str, Any] = {}

            if req.action_type == BrowserActionType.NAVIGATE:
                url = req.parameters.get("url")
                if not url:
                    raise ValueError("Navigation requires 'url' in parameters.")
                wait_until = req.parameters.get("wait_until", "domcontentloaded")
                response = await page.goto(url, wait_until=wait_until, timeout=timeout)
                result_data = {
                    "url": page.url,
                    "title": await page.title(),
                    "status_code": response.status if response else None,
                }

            elif req.action_type == BrowserActionType.CLICK:
                if not req.target_locator:
                    raise ValueError("Click action requires 'target_locator'.")
                loc = LocatorResolver.resolve(page, req.target_locator)
                await loc.click(timeout=timeout)
                result_data = {
                    "clicked_locator": req.target_locator,
                    "new_url": page.url,
                }

            elif req.action_type == BrowserActionType.FILL:
                if not req.target_locator:
                    raise ValueError("Fill action requires 'target_locator'.")
                value = req.parameters.get("value", "")
                loc = LocatorResolver.resolve(page, req.target_locator)
                await loc.fill(str(value), timeout=timeout)
                result_data = {
                    "filled_locator": req.target_locator,
                    "value_length": len(str(value)),
                }

            elif req.action_type == BrowserActionType.SELECT:
                if not req.target_locator:
                    raise ValueError("Select action requires 'target_locator'.")
                value = req.parameters.get("value")
                loc = LocatorResolver.resolve(page, req.target_locator)
                selected = await loc.select_option(value, timeout=timeout)
                result_data = {
                    "selected_values": selected,
                }

            elif req.action_type == BrowserActionType.CHECK:
                if not req.target_locator:
                    raise ValueError("Check action requires 'target_locator'.")
                checked = req.parameters.get("checked", True)
                loc = LocatorResolver.resolve(page, req.target_locator)
                if checked:
                    await loc.check(timeout=timeout)
                else:
                    await loc.uncheck(timeout=timeout)
                result_data = {
                    "is_checked": checked,
                }

            elif req.action_type == BrowserActionType.PRESS_KEY:
                key = req.parameters.get("key", "Enter")
                if req.target_locator:
                    loc = LocatorResolver.resolve(page, req.target_locator)
                    await loc.press(key, timeout=timeout)
                else:
                    await page.keyboard.press(key)
                result_data = {
                    "key_pressed": key,
                }

            elif req.action_type == BrowserActionType.HOVER:
                if not req.target_locator:
                    raise ValueError("Hover action requires 'target_locator'.")
                loc = LocatorResolver.resolve(page, req.target_locator)
                await loc.hover(timeout=timeout)
                result_data = {
                    "hovered_locator": req.target_locator,
                }

            elif req.action_type == BrowserActionType.SCROLL:
                direction = req.parameters.get("direction", "down")
                amount = req.parameters.get("amount", 400)
                delta_y = amount if direction == "down" else -amount if direction == "up" else 0
                delta_x = amount if direction == "right" else -amount if direction == "left" else 0
                await page.mouse.wheel(delta_x, delta_y)
                result_data = {
                    "direction": direction,
                    "amount": amount,
                }

            elif req.action_type == BrowserActionType.EVALUATE:
                script = req.parameters.get("script")
                if not script:
                    raise ValueError("Evaluate action requires 'script'.")
                eval_res = await page.evaluate(script)
                result_data = {
                    "evaluation_result": eval_res,
                }

            else:
                raise NotImplementedError(f"Unsupported action type: {req.action_type}")

            duration_ms = (time.perf_counter() - start_time) * 1000
            return BrowserActionResponse(
                id=action_id,
                session_id=session_id,
                tab_id=tab_id,
                action_type=req.action_type,
                status=BrowserActionStatus.SUCCEEDED,
                result=result_data,
                error_message=None,
                screenshot_path=None,
                duration_ms=round(duration_ms, 2),
            )

        except PlaywrightTimeoutError as te:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.warning(f"Timeout executing action {req.action_type} on {req.target_locator}: {te}")
            return BrowserActionResponse(
                id=action_id,
                session_id=session_id,
                tab_id=tab_id,
                action_type=req.action_type,
                status=BrowserActionStatus.FAILED,
                result=None,
                error_message=f"Action timed out after {timeout}ms: {te}",
                screenshot_path=None,
                duration_ms=round(duration_ms, 2),
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Error executing action {req.action_type}: {exc}")
            return BrowserActionResponse(
                id=action_id,
                session_id=session_id,
                tab_id=tab_id,
                action_type=req.action_type,
                status=BrowserActionStatus.FAILED,
                result=None,
                error_message=str(exc),
                screenshot_path=None,
                duration_ms=round(duration_ms, 2),
            )
