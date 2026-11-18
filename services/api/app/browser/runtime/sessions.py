"""Browser session manager managing active Playwright contexts and persistence."""

import asyncio
from datetime import datetime, timezone
import logging
from typing import Any
from uuid import uuid4

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.contracts import (
    BrowserSessionCreateRequest,
    BrowserSessionResponse,
    BrowserSessionStatus,
    BrowserSessionSummary,
    BrowserTabInfo,
    BrowserTabStatus,
    BrowserType,
)
from app.browser.runtime.manager import BrowserRuntimeManager
from app.browser.runtime.tabs import TabManager, LiveTab
from app.browser.security.authentication import BrowserAuthenticationManager
from app.core.config import settings
from app.db.models import BrowserSessionRecord, BrowserTabRecord

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LiveSession:
    """Represents an active, in-memory Playwright browser session."""

    def __init__(
        self,
        session_id: str,
        playwright_cm: Any,
        playwright_instance: Playwright,
        browser: Browser,
        context: BrowserContext,
        tab_manager: TabManager,
        profile_id: str | None,
        browser_type: str,
        channel: str | None,
        is_headless: bool,
        viewport_width: int,
        viewport_height: int,
        user_agent: str | None,
        locale: str,
        timezone_id: str,
        metadata: dict[str, Any],
    ) -> None:
        self.session_id = session_id
        self.playwright_cm = playwright_cm
        self.playwright_instance = playwright_instance
        self.browser = browser
        self.context = context
        self.tab_manager = tab_manager
        self.profile_id = profile_id
        self.browser_type = browser_type
        self.channel = channel
        self.is_headless = is_headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = user_agent
        self.locale = locale
        self.timezone_id = timezone_id
        self.metadata = metadata
        self.status = BrowserSessionStatus.RUNNING
        self.created_at = utc_now()
        self.last_activity_at = utc_now()
        self.closed_at: datetime | None = None
        self.error_message: str | None = None
        self._lock = asyncio.Lock()

    def touch(self) -> None:
        self.last_activity_at = utc_now()

    def get_active_page(self) -> Page:
        tab = self.tab_manager.get_active_tab()
        if not tab or tab.page.is_closed():
            # If no active tab or it closed, pick first available
            for t in self.tab_manager.tabs.values():
                if not t.page.is_closed():
                    self.tab_manager.set_active_tab(t.tab_id)
                    return t.page
            raise RuntimeError(f"Session {self.session_id} has no open tabs.")
        return tab.page

    async def to_response(self) -> BrowserSessionResponse:
        tabs_info = await self.tab_manager.list_tabs_info()
        return BrowserSessionResponse(
            id=self.session_id,
            profile_id=self.profile_id,
            browser_type=self.browser_type,
            channel=self.channel,
            status=self.status,
            is_headless=self.is_headless,
            active_tab_id=self.tab_manager.active_tab_id,
            pid=None,
            viewport_width=self.viewport_width,
            viewport_height=self.viewport_height,
            user_agent=self.user_agent,
            locale=self.locale,
            timezone_id=self.timezone_id,
            created_at=self.created_at,
            last_activity_at=self.last_activity_at,
            closed_at=self.closed_at,
            error_message=self.error_message,
            metadata=self.metadata,
            tabs=tabs_info,
        )


class BrowserSessionManager:
    """Coordinates browser session lifecycles, active contexts, and persistence."""

    def __init__(
        self,
        runtime_manager: BrowserRuntimeManager | None = None,
        auth_manager: BrowserAuthenticationManager | None = None,
    ) -> None:
        self.runtime_manager = runtime_manager or BrowserRuntimeManager()
        self.auth_manager = auth_manager or BrowserAuthenticationManager()
        self.active_sessions: dict[str, LiveSession] = {}
        self._lock = asyncio.Lock()

    def get_live_session(self, session_id: str) -> LiveSession | None:
        """Retrieves an in-memory active session."""
        return self.active_sessions.get(session_id)

    async def create_session(
        self,
        db_session: AsyncSession,
        req: BrowserSessionCreateRequest,
    ) -> BrowserSessionResponse:
        """Launches a new isolated browser context and tracks it in DB and memory."""
        session_id = str(uuid4())
        settings.ensure_directories()

        pw_cm = async_playwright()
        pw = await pw_cm.start()

        launch_opts = self.runtime_manager.resolve_launch_options(
            browser_type=req.browser_type,
            channel=req.channel,
            is_headless=req.is_headless,
        )

        try:
            # Launch requested browser engine (Chromium default, fallback to chromium if edge fails)
            try:
                browser = await pw.chromium.launch(**launch_opts)
            except Exception as launch_exc:
                logger.warning(f"Failed to launch with channel {launch_opts.get('channel')}: {launch_exc}. Falling back to default chromium.")
                if "channel" in launch_opts:
                    del launch_opts["channel"]
                    browser = await pw.chromium.launch(**launch_opts)
                else:
                    raise launch_exc

            # Check if storage state exists for profile
            storage_state_file: str | None = None
            if req.profile_id:
                storage_state_file = self.auth_manager.export_temporary_state_file(req.profile_id)

            context_opts: dict[str, Any] = {
                "viewport": {"width": req.viewport_width, "height": req.viewport_height},
                "locale": req.locale,
                "timezone_id": req.timezone_id,
                "accept_downloads": True,
            }
            if req.user_agent:
                context_opts["user_agent"] = req.user_agent
            if storage_state_file:
                context_opts["storage_state"] = storage_state_file

            context = await browser.new_context(**context_opts)

            if storage_state_file:
                self.auth_manager.cleanup_temporary_state_file(req.profile_id)

            tab_manager = TabManager(session_id=session_id, context=context)
            initial_page = await context.new_page()
            initial_tab = tab_manager.register_initial_page(initial_page)

            live_session = LiveSession(
                session_id=session_id,
                playwright_cm=pw_cm,
                playwright_instance=pw,
                browser=browser,
                context=context,
                tab_manager=tab_manager,
                profile_id=req.profile_id,
                browser_type=req.browser_type.value,
                channel=req.channel,
                is_headless=req.is_headless,
                viewport_width=req.viewport_width,
                viewport_height=req.viewport_height,
                user_agent=req.user_agent,
                locale=req.locale,
                timezone_id=req.timezone_id,
                metadata=req.metadata,
            )

            # Persist records in DB
            session_record = BrowserSessionRecord(
                id=session_id,
                profile_id=req.profile_id,
                browser_type=req.browser_type.value,
                channel=req.channel,
                status=BrowserSessionStatus.RUNNING.value,
                is_headless=req.is_headless,
                active_tab_id=initial_tab.tab_id,
                pid=None,
                viewport_width=req.viewport_width,
                viewport_height=req.viewport_height,
                user_agent=req.user_agent,
                locale=req.locale,
                timezone_id=req.timezone_id,
                created_at=live_session.created_at,
                last_activity_at=live_session.last_activity_at,
                closed_at=None,
                error_message=None,
                metadata_json=req.metadata,
            )
            tab_record = BrowserTabRecord(
                id=initial_tab.tab_id,
                session_id=session_id,
                tab_index=0,
                title="",
                url="about:blank",
                status=BrowserTabStatus.READY.value,
                is_active=True,
                created_at=initial_tab.created_at,
                updated_at=initial_tab.updated_at,
                closed_at=None,
            )

            db_session.add(session_record)
            db_session.add(tab_record)
            await db_session.commit()

            async with self._lock:
                self.active_sessions[session_id] = live_session

            logger.info(f"Launched browser session {session_id} ({req.browser_type.value}, headless={req.is_headless})")
            return await live_session.to_response()

        except Exception as exc:
            logger.error(f"Failed to create browser session: {exc}", exc_info=True)
            try:
                await pw.stop()
            except Exception:
                pass
            raise exc

    async def close_session(self, db_session: AsyncSession, session_id: str) -> bool:
        """Gracefully closes an active session and updates DB status."""
        async with self._lock:
            live = self.active_sessions.pop(session_id, None)

        if live:
            live.status = BrowserSessionStatus.CLOSED
            live.closed_at = utc_now()
            try:
                await live.context.close()
            except Exception as e:
                logger.debug(f"Error closing context for {session_id}: {e}")
            try:
                await live.browser.close()
            except Exception as e:
                logger.debug(f"Error closing browser for {session_id}: {e}")
            try:
                await live.playwright_instance.stop()
            except Exception as e:
                logger.debug(f"Error stopping playwright for {session_id}: {e}")

        # Update DB record
        stmt = (
            update(BrowserSessionRecord)
            .where(BrowserSessionRecord.id == session_id)
            .values(
                status=BrowserSessionStatus.CLOSED.value,
                closed_at=utc_now(),
                last_activity_at=utc_now(),
            )
        )
        await db_session.execute(stmt)
        await db_session.commit()
        logger.info(f"Closed browser session {session_id}")
        return True

    async def close_all_sessions(self, db_session: AsyncSession | None = None) -> None:
        """Closes all active sessions on shutdown or emergency stop."""
        async with self._lock:
            session_ids = list(self.active_sessions.keys())

        for sid in session_ids:
            try:
                if db_session:
                    await self.close_session(db_session, sid)
                else:
                    live = self.active_sessions.pop(sid, None)
                    if live:
                        await live.context.close()
                        await live.browser.close()
                        await live.playwright_instance.stop()
            except Exception as exc:
                logger.warning(f"Error closing session {sid} on mass shutdown: {exc}")

    async def list_session_summaries(self, db_session: AsyncSession) -> list[BrowserSessionSummary]:
        """Lists summaries of recent sessions from database."""
        stmt = select(BrowserSessionRecord).order_by(BrowserSessionRecord.created_at.desc()).limit(50)
        res = await db_session.execute(stmt)
        records = res.scalars().all()

        summaries: list[BrowserSessionSummary] = []
        for r in records:
            live = self.active_sessions.get(r.id)
            tab_count = len(live.tab_manager.tabs) if live else 0
            cur_url = ""
            cur_title = ""
            if live:
                active_tab = live.tab_manager.get_active_tab()
                if active_tab:
                    cur_url = active_tab.url
                    cur_title = active_tab.title

            summaries.append(
                BrowserSessionSummary(
                    id=r.id,
                    browser_type=r.browser_type,
                    channel=r.channel,
                    status=BrowserSessionStatus(r.status) if r.status in BrowserSessionStatus._value2member_map_ else BrowserSessionStatus.CLOSED,
                    is_headless=r.is_headless,
                    active_tab_id=r.active_tab_id,
                    tab_count=tab_count,
                    current_url=cur_url,
                    current_title=cur_title,
                    created_at=r.created_at,
                    last_activity_at=r.last_activity_at,
                )
            )
        return summaries
