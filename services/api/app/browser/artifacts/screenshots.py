"""Screenshot capture and thumbnail generation for browser automation diagnostics."""

import base64
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from playwright.async_api import Page

from app.browser.contracts import BrowserScreenshotRequest, BrowserScreenshotResponse
from app.browser.interaction.locators import LocatorResolver
from app.core.config import settings

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BrowserScreenshotManager:
    """Manages full-page and element screenshots with base64 thumbnail encoding."""

    def __init__(self, screenshots_dir: Path | None = None) -> None:
        self.screenshots_dir = screenshots_dir or settings.browser_screenshots_dir
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    async def capture(
        self,
        page: Page,
        session_id: str,
        tab_id: str,
        req: BrowserScreenshotRequest | None = None,
    ) -> BrowserScreenshotResponse:
        """Captures a screenshot from the page or target element."""
        req = req or BrowserScreenshotRequest()
        screenshot_id = str(uuid4())
        filename = f"{session_id[:8]}_{tab_id[:8]}_{screenshot_id[:8]}.png"
        file_path = self.screenshots_dir / filename

        opts: dict = {
            "type": "png",
            "path": str(file_path),
        }

        if req.element_locator:
            loc = LocatorResolver.resolve(page, req.element_locator)
            raw_bytes = await loc.screenshot(**opts)
        else:
            opts["full_page"] = req.full_page
            raw_bytes = await page.screenshot(**opts)

        viewport = page.viewport_size or {"width": 1280, "height": 800}
        width = viewport.get("width", 1280)
        height = viewport.get("height", 800)

        # Base64 thumbnail for frontend rendering
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        data_uri = f"data:image/png;base64,{b64_str}"

        logger.info(f"Captured screenshot {filename} ({width}x{height})")

        return BrowserScreenshotResponse(
            session_id=session_id,
            tab_id=tab_id,
            screenshot_path=str(file_path),
            thumbnail_base64=data_uri,
            width=width,
            height=height,
            captured_at=utc_now(),
        )
