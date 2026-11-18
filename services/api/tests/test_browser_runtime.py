"""Runtime tests for Playwright browser context, session, and tab management."""

import pytest
from app.browser.contracts import BrowserSessionCreateRequest, BrowserType
from app.browser.runtime.manager import BrowserRuntimeManager
from app.browser.service import BrowserService
from app.db.engine import get_db_session
from app.security.authorization.emergency import EmergencyStopController


@pytest.mark.asyncio
async def test_browser_runtime_manager_detection():
    mgr = BrowserRuntimeManager()
    assert mgr.playwright_available is True
    installed = mgr.detect_installed_browsers()
    assert "chromium" in installed
    status = mgr.get_runtime_status(active_sessions_count=1)
    assert status.playwright_available is True
    assert status.active_sessions_count == 1
    assert status.default_headless is True


@pytest.mark.asyncio
async def test_browser_session_lifecycle():
    await EmergencyStopController.get_instance().clear_emergency_stop("test_setup")
    service = BrowserService.get_instance()
    async with get_db_session() as db:
        # 1. Create headless session
        req = BrowserSessionCreateRequest(
            browser_type=BrowserType.CHROMIUM,
            is_headless=True,
            viewport_width=1024,
            viewport_height=768,
        )
        session_resp = await service.create_session(db, req)
        assert session_resp.id is not None
        assert session_resp.status.value == "running"
        assert len(session_resp.tabs) == 1
        initial_tab_id = session_resp.tabs[0].id

        # 2. Check in-memory live session
        live = service.session_manager.get_live_session(session_resp.id)
        assert live is not None
        assert live.is_headless is True

        # 3. Create second tab
        tab2 = await service.create_tab(db, session_resp.id)
        assert tab2.id is not None
        assert len(live.tab_manager.tabs) == 2

        # 4. Switch active tab
        switch_ok = await service.switch_tab(session_resp.id, initial_tab_id)
        assert switch_ok is True
        assert live.tab_manager.active_tab_id == initial_tab_id

        # 5. Close tab2
        close_tab_ok = await service.close_tab(session_resp.id, tab2.id)
        assert close_tab_ok is True

        # 6. Close entire session
        close_sess_ok = await service.close_session(db, session_resp.id)
        assert close_sess_ok is True
        assert service.session_manager.get_live_session(session_resp.id) is None


@pytest.mark.asyncio
async def test_browser_service_emergency_stop_blocks_operations():
    service = BrowserService.get_instance()
    controller = EmergencyStopController.get_instance()

    # Activate emergency stop
    await controller.activate_emergency_stop(activated_by="test_admin", reason="Security drill")
    assert controller.is_emergency_stop_active is True

    try:
        async with get_db_session() as db:
            with pytest.raises(RuntimeError) as exc_info:
                await service.create_session(db, BrowserSessionCreateRequest())
            assert "Emergency Stop is currently active" in str(exc_info.value)
    finally:
        # Reset emergency stop
        await controller.clear_emergency_stop(cleared_by="test_admin")
        assert controller.is_emergency_stop_active is False
