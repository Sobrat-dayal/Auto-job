"""Tab and window management for browser sessions."""

import asyncio
from datetime import datetime, timezone
import logging
from typing import Callable, Any
from uuid import uuid4

from playwright.async_api import Page, BrowserContext

from app.browser.contracts import BrowserTabInfo, BrowserTabStatus

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LiveTab:
    """Encapsulates a live Playwright page tab."""

    def __init__(
        self,
        tab_id: str,
        session_id: str,
        tab_index: int,
        page: Page,
        on_close_cb: Callable[[str], None] | None = None,
    ) -> None:
        self.tab_id = tab_id
        self.session_id = session_id
        self.tab_index = tab_index
        self.page = page
        self.title: str = ""
        self.url: str = ""
        self.status: BrowserTabStatus = BrowserTabStatus.READY
        self.is_active: bool = False
        self.created_at: datetime = utc_now()
        self.updated_at: datetime = utc_now()
        self.closed_at: datetime | None = None
        self._on_close_cb = on_close_cb

        # Wire page events
        self.page.on("close", self._handle_page_close)
        self.page.on("crash", self._handle_page_crash)

    def _handle_page_close(self, page: Page) -> None:
        self.status = BrowserTabStatus.CLOSED
        self.closed_at = utc_now()
        self.updated_at = utc_now()
        logger.info(f"Tab {self.tab_id} closed in session {self.session_id}")
        if self._on_close_cb:
            self._on_close_cb(self.tab_id)

    def _handle_page_crash(self, page: Page) -> None:
        self.status = BrowserTabStatus.CRASHED
        self.updated_at = utc_now()
        logger.error(f"Tab {self.tab_id} crashed in session {self.session_id}")

    async def update_info(self) -> None:
        """Refreshes title and url from the live page."""
        if self.page.is_closed():
            self.status = BrowserTabStatus.CLOSED
            return
        try:
            self.url = self.page.url
            self.title = await self.page.title()
            self.updated_at = utc_now()
        except Exception as exc:
            logger.debug(f"Could not refresh tab info for {self.tab_id}: {exc}")

    def to_tab_info(self) -> BrowserTabInfo:
        return BrowserTabInfo(
            id=self.tab_id,
            session_id=self.session_id,
            tab_index=self.tab_index,
            title=self.title,
            url=self.url,
            status=self.status,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
            closed_at=self.closed_at,
        )


class TabManager:
    """Manages tabs within a browser context."""

    def __init__(self, session_id: str, context: BrowserContext) -> None:
        self.session_id = session_id
        self.context = context
        self.tabs: dict[str, LiveTab] = {}
        self.active_tab_id: str | None = None

        # Listen for popup / new tabs spawned by window.open or target="_blank"
        self.context.on("page", self._handle_new_popup_page)

    def _handle_new_popup_page(self, page: Page) -> None:
        # Check if already registered
        if any(t.page == page for t in self.tabs.values()):
            return
        tab_id = str(uuid4())
        index = len(self.tabs)
        live_tab = LiveTab(
            tab_id=tab_id,
            session_id=self.session_id,
            tab_index=index,
            page=page,
            on_close_cb=self._on_tab_closed,
        )
        self.tabs[tab_id] = live_tab
        logger.info(f"Captured new popup page as tab {tab_id} in session {self.session_id}")

    def _on_tab_closed(self, tab_id: str) -> None:
        if self.active_tab_id == tab_id:
            # Switch to another available tab if one exists
            remaining = [t for t_id, t in self.tabs.items() if t_id != tab_id and not t.page.is_closed()]
            if remaining:
                self.set_active_tab(remaining[0].tab_id)
            else:
                self.active_tab_id = None

    async def create_tab(self, url: str | None = None) -> LiveTab:
        """Opens a new tab in the browser context."""
        page = await self.context.new_page()
        # Find the registered tab from event or create if needed
        live_tab = next((t for t in self.tabs.values() if t.page == page), None)
        if not live_tab:
            tab_id = str(uuid4())
            index = len(self.tabs)
            live_tab = LiveTab(
                tab_id=tab_id,
                session_id=self.session_id,
                tab_index=index,
                page=page,
                on_close_cb=self._on_tab_closed,
            )
            self.tabs[tab_id] = live_tab

        if url:
            await page.goto(url)
            await live_tab.update_info()

        # If active is None or single tab, activate it
        if not self.active_tab_id or len(self.tabs) == 1:
            self.set_active_tab(live_tab.tab_id)

        return live_tab

    def register_initial_page(self, page: Page) -> LiveTab:
        """Registers the initial page created when context was created."""
        live_tab = next((t for t in self.tabs.values() if t.page == page), None)
        if not live_tab:
            tab_id = str(uuid4())
            live_tab = LiveTab(
                tab_id=tab_id,
                session_id=self.session_id,
                tab_index=0,
                page=page,
                on_close_cb=self._on_tab_closed,
            )
            self.tabs[tab_id] = live_tab

        live_tab.is_active = True
        self.active_tab_id = live_tab.tab_id
        return live_tab

    def set_active_tab(self, tab_id: str) -> bool:
        """Sets the currently active tab."""
        if tab_id not in self.tabs:
            return False
        for tid, tab in self.tabs.items():
            tab.is_active = (tid == tab_id)
        self.active_tab_id = tab_id
        return True

    def get_active_tab(self) -> LiveTab | None:
        """Returns the active tab."""
        if not self.active_tab_id or self.active_tab_id not in self.tabs:
            return None
        return self.tabs[self.active_tab_id]

    async def close_tab(self, tab_id: str) -> bool:
        """Closes a specific tab."""
        if tab_id not in self.tabs:
            return False
        tab = self.tabs[tab_id]
        if not tab.page.is_closed():
            await tab.page.close()
        tab.status = BrowserTabStatus.CLOSED
        tab.closed_at = utc_now()
        self._on_tab_closed(tab_id)
        return True

    async def list_tabs_info(self) -> list[BrowserTabInfo]:
        """Returns metadata for all tabs."""
        infos: list[BrowserTabInfo] = []
        for tab in self.tabs.values():
            await tab.update_info()
            infos.append(tab.to_tab_info())
        return infos
