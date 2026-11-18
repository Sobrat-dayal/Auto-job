"""Browser Automation API endpoints for AUTONOM Stage 16."""

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AuthDep
from app.browser.contracts import (
    BrowserActionRequest,
    BrowserActionResponse,
    BrowserBatchActionsRequest,
    BrowserBatchActionsResponse,
    BrowserDownloadResponse,
    BrowserNavigateRequest,
    BrowserNavigateResponse,
    BrowserProfileCreateRequest,
    BrowserProfileResponse,
    BrowserRuntimeStatus,
    BrowserScreenshotRequest,
    BrowserScreenshotResponse,
    BrowserSessionCreateRequest,
    BrowserSessionResponse,
    BrowserSessionSummary,
    BrowserTabCreateRequest,
    BrowserTabInfo,
    BrowserTabSwitchRequest,
    BrowserTaskCreateRequest,
    BrowserTaskResponse,
    DOMInspectionRequest,
    DOMInspectionResponse,
)
from app.browser.service import BrowserService
from app.db.engine import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/browser", tags=["browser"])


def get_browser_service() -> BrowserService:
    return BrowserService.get_instance()


@router.get("/status", response_model=BrowserRuntimeStatus)
async def get_browser_status(
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserRuntimeStatus:
    """Returns runtime telemetry, installed browser engines, and system diagnostics."""
    return service.get_runtime_status()


@router.get("/sessions", response_model=list[BrowserSessionSummary])
async def list_browser_sessions(
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> list[BrowserSessionSummary]:
    """Lists summaries of active and recent browser sessions."""
    async with get_db_session() as db:
        return await service.list_sessions(db)


@router.post("/sessions", response_model=BrowserSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_browser_session(
    request: BrowserSessionCreateRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserSessionResponse:
    """Launches a new browser context with isolated session state and tab management."""
    try:
        async with get_db_session() as db:
            return await service.create_session(db, request)
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(re))
    except Exception as exc:
        logger.error(f"Failed to create browser session: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to launch browser: {exc}")


@router.get("/sessions/{session_id}", response_model=BrowserSessionResponse)
async def get_browser_session(
    session_id: str,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserSessionResponse:
    """Retrieves detailed session state, active tabs, and metadata."""
    async with get_db_session() as db:
        sess = await service.get_session(db, session_id)
        if not sess:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found.")
        return sess


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_browser_session(
    session_id: str,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> None:
    """Gracefully closes a browser session and frees all context resources."""
    async with get_db_session() as db:
        await service.close_session(db, session_id)


@router.post("/sessions/{session_id}/navigate", response_model=BrowserNavigateResponse)
async def navigate_browser_session(
    session_id: str,
    request: BrowserNavigateRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserNavigateResponse:
    """Safely navigates the active browser tab to a validated URL."""
    try:
        async with get_db_session() as db:
            return await service.navigate(db, session_id, request)
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(re))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Navigation failed: {exc}")


@router.get("/sessions/{session_id}/page")
async def get_active_page_info(
    session_id: str,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> dict[str, Any]:
    """Returns current active tab URL and title."""
    live = service.session_manager.get_live_session(session_id)
    if not live:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} is not active.")
    active_tab = live.tab_manager.get_active_tab()
    if not active_tab:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active tab in session.")
    await active_tab.update_info()
    return {
        "session_id": session_id,
        "tab_id": active_tab.tab_id,
        "title": active_tab.title,
        "url": active_tab.url,
        "status": active_tab.status.value,
    }


@router.post("/sessions/{session_id}/inspect", response_model=DOMInspectionResponse)
async def inspect_browser_dom(
    session_id: str,
    _auth: AuthDep,
    request: DOMInspectionRequest = DOMInspectionRequest(),
    service: BrowserService = Depends(get_browser_service),
) -> DOMInspectionResponse:
    """Inspects page structure, extracting compact interactive element nodes and forms."""
    try:
        return await service.inspect_dom(session_id, request)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DOM inspection failed: {exc}")


@router.post("/sessions/{session_id}/actions", response_model=BrowserActionResponse)
async def execute_browser_action(
    session_id: str,
    request: BrowserActionRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserActionResponse:
    """Executes a single browser action (click, fill, select, check, press_key, scroll, hover)."""
    try:
        async with get_db_session() as db:
            return await service.execute_action(db, session_id, request)
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(re))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Action failed: {exc}")


@router.post("/sessions/{session_id}/batch-actions", response_model=BrowserBatchActionsResponse)
async def execute_batch_browser_actions(
    session_id: str,
    request: BrowserBatchActionsRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserBatchActionsResponse:
    """Executes a series of browser actions sequentially."""
    try:
        async with get_db_session() as db:
            return await service.execute_batch_actions(db, session_id, request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Batch execution failed: {exc}")


@router.post("/sessions/{session_id}/screenshot", response_model=BrowserScreenshotResponse)
async def capture_browser_screenshot(
    session_id: str,
    _auth: AuthDep,
    request: BrowserScreenshotRequest = BrowserScreenshotRequest(),
    service: BrowserService = Depends(get_browser_service),
) -> BrowserScreenshotResponse:
    """Captures a screenshot of the active view or target element."""
    try:
        return await service.capture_screenshot(session_id, request)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Screenshot failed: {exc}")


@router.get("/sessions/{session_id}/tabs", response_model=list[BrowserTabInfo])
async def list_session_tabs(
    session_id: str,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> list[BrowserTabInfo]:
    """Lists all open tabs in a browser session."""
    live = service.session_manager.get_live_session(session_id)
    if not live:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} is not active.")
    return await live.tab_manager.list_tabs_info()


@router.post("/sessions/{session_id}/tabs", response_model=BrowserTabInfo, status_code=status.HTTP_201_CREATED)
async def create_session_tab(
    session_id: str,
    _auth: AuthDep,
    request: BrowserTabCreateRequest = BrowserTabCreateRequest(),
    service: BrowserService = Depends(get_browser_service),
) -> BrowserTabInfo:
    """Opens a new tab in the specified browser session."""
    try:
        async with get_db_session() as db:
            return await service.create_tab(db, session_id, request)
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.put("/sessions/{session_id}/tabs/switch")
async def switch_session_tab(
    session_id: str,
    request: BrowserTabSwitchRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> dict[str, Any]:
    """Switches the active tab in a session."""
    success = await service.switch_tab(session_id, request.tab_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tab {request.tab_id} not found.")
    return {"session_id": session_id, "active_tab_id": request.tab_id, "success": True}


@router.delete("/sessions/{session_id}/tabs/{tab_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_session_tab(
    session_id: str,
    tab_id: str,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> None:
    """Closes a specific tab in a session."""
    success = await service.close_tab(session_id, tab_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tab {tab_id} not found.")


@router.get("/profiles", response_model=list[BrowserProfileResponse])
async def list_browser_profiles(
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> list[BrowserProfileResponse]:
    """Lists saved browser profiles with domain scopes."""
    async with get_db_session() as db:
        return await service.list_profiles(db)


@router.post("/profiles", response_model=BrowserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_browser_profile(
    request: BrowserProfileCreateRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserProfileResponse:
    """Creates a new browser profile record."""
    async with get_db_session() as db:
        return await service.create_profile(db, request)


@router.get("/downloads", response_model=list[BrowserDownloadResponse])
async def list_browser_downloads(
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> list[BrowserDownloadResponse]:
    """Lists tracked file downloads with SHA-256 integrity checksums."""
    async with get_db_session() as db:
        return await service.list_downloads(db)


@router.get("/tasks", response_model=list[BrowserTaskResponse])
async def list_browser_tasks(
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> list[BrowserTaskResponse]:
    """Lists recent browser automation tasks."""
    async with get_db_session() as db:
        return await service.list_tasks(db)


@router.post("/tasks", response_model=BrowserTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_browser_task(
    request: BrowserTaskCreateRequest,
    _auth: AuthDep,
    service: BrowserService = Depends(get_browser_service),
) -> BrowserTaskResponse:
    """Registers a goal-driven browser automation task."""
    try:
        async with get_db_session() as db:
            return await service.create_task(db, request)
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(re))

