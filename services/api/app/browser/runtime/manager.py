"""Browser runtime manager for detecting, launching, and managing browser engines."""

import logging
import os
import shutil
from pathlib import Path
from typing import Any

from app.browser.contracts import BrowserRuntimeStatus, BrowserType
from app.core.config import settings

logger = logging.getLogger(__name__)

WINDOWS_EDGE_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

WINDOWS_CHROME_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")),
]


class BrowserRuntimeManager:
    """Manages browser discovery, binaries, and runtime health."""

    def __init__(self) -> None:
        self.playwright_available = False
        try:
            import playwright.async_api  # noqa: F401
            self.playwright_available = True
        except ImportError:
            self.playwright_available = False

    def detect_system_browsers(self) -> list[str]:
        """Detects system-installed browsers on Windows."""
        browsers: list[str] = []
        for p in WINDOWS_EDGE_PATHS:
            if p.exists():
                browsers.append("msedge")
                break
        for p in WINDOWS_CHROME_PATHS:
            if p.exists():
                browsers.append("chrome")
                break
        return browsers

    def detect_installed_browsers(self) -> list[str]:
        """Returns the list of supported and installed browser engines."""
        installed: list[str] = []
        if self.playwright_available:
            installed.append("chromium")

        system_browsers = self.detect_system_browsers()
        if "msedge" in system_browsers:
            installed.append("msedge")
        if "chrome" in system_browsers:
            installed.append("chrome")
        return installed

    def get_runtime_status(self, active_sessions_count: int = 0) -> BrowserRuntimeStatus:
        """Returns telemetry and runtime diagnostics for the browser automation engine."""
        installed = self.detect_installed_browsers()
        system = self.detect_system_browsers()

        return BrowserRuntimeStatus(
            playwright_available=self.playwright_available,
            installed_browsers=installed,
            system_browsers_detected=system,
            active_sessions_count=active_sessions_count,
            max_concurrent_sessions=5,
            default_headless=True,
            downloads_dir=str(settings.browser_downloads_dir),
            screenshots_dir=str(settings.browser_screenshots_dir),
        )

    def resolve_launch_options(
        self,
        browser_type: BrowserType,
        channel: str | None = None,
        is_headless: bool = True,
        slow_mo_ms: int = 0,
    ) -> dict[str, Any]:
        """Builds safe launch arguments for Playwright browser launcher."""
        options: dict[str, Any] = {
            "headless": is_headless,
            "slow_mo": slow_mo_ms,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-first-run",
            ],
        }

        # Resolve channel if edge or chrome requested
        if browser_type == BrowserType.MSEDGE or channel == "msedge":
            options["channel"] = "msedge"
        elif browser_type == BrowserType.CHROME or channel == "chrome":
            options["channel"] = "chrome"
        elif channel:
            options["channel"] = channel

        return options
