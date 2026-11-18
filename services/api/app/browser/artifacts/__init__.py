"""Browser artifacts package for downloads, screenshots, and traces."""

from app.browser.artifacts.downloads import BrowserDownloadManager
from app.browser.artifacts.screenshots import BrowserScreenshotManager
from app.browser.artifacts.traces import BrowserTraceManager

__all__ = ["BrowserDownloadManager", "BrowserScreenshotManager", "BrowserTraceManager"]
