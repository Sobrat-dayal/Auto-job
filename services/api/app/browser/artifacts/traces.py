"""Playwright trace recording for deep diagnostic and audit replays."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from playwright.async_api import BrowserContext

from app.core.config import settings

logger = logging.getLogger(__name__)


class BrowserTraceManager:
    """Manages zip trace recordings for browser contexts."""

    def __init__(self, traces_dir: Path | None = None) -> None:
        self.traces_dir = traces_dir or settings.browser_traces_dir
        self.traces_dir.mkdir(parents=True, exist_ok=True)

    async def start_trace(self, context: BrowserContext, session_id: str) -> None:
        """Begins recording actions, DOM snapshots, and screenshots."""
        try:
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)
            logger.info(f"Started trace recording for session {session_id}")
        except Exception as exc:
            logger.warning(f"Failed to start tracing for session {session_id}: {exc}")

    async def stop_trace(self, context: BrowserContext, session_id: str) -> str | None:
        """Stops recording and saves trace zip archive."""
        trace_id = str(uuid4())
        dest_file = self.traces_dir / f"{session_id[:8]}_{trace_id[:8]}.zip"
        try:
            await context.tracing.stop(path=str(dest_file))
            logger.info(f"Saved trace file to {dest_file}")
            return str(dest_file)
        except Exception as exc:
            logger.warning(f"Failed to stop trace recording for session {session_id}: {exc}")
            return None
