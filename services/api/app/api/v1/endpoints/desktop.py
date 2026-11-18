"""FastAPI REST endpoints for Windows Structural UI Automation (Stage 17)."""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.security import require_auth
from app.computer.contracts import (
    DesktopActionRequest,
    DesktopActionResult,
    DesktopApplicationInfo,
    DesktopDiagnosticsInfo,
    DesktopSessionInfo,
    DesktopTaskRequest,
    DesktopTaskResponse,
    ElementQuery,
    InspectionOptions,
    UIElementInfo,
    UITreeSnapshot,
    WindowInfo,
    WindowManageAction,
)
from app.computer.service import desktop_service

router = APIRouter(prefix="/desktop", tags=["desktop"], dependencies=[Depends(require_auth)])


class WindowManageRequest(BaseModel):
    action: WindowManageAction


class AppLaunchRequest(BaseModel):
    executable_name: str
    arguments: list[str] = []


class ElementSearchRequest(BaseModel):
    window_ref: str
    query: ElementQuery


@router.get("/status")
async def get_desktop_status() -> dict[str, Any]:
    """Returns desktop automation status and active session info."""
    diag = desktop_service.get_diagnostics()
    return diag.model_dump()


@router.get("/session", response_model=DesktopSessionInfo)
async def get_session() -> DesktopSessionInfo:
    """Returns interactive desktop session telemetry."""
    return desktop_service.get_session_info()


@router.get("/applications", response_model=list[DesktopApplicationInfo])
async def list_applications() -> list[DesktopApplicationInfo]:
    """Lists running desktop applications."""
    try:
        return desktop_service.list_applications()
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/applications/launch", response_model=WindowInfo | None)
async def launch_application(request: AppLaunchRequest) -> WindowInfo | None:
    """Launches an approved desktop application and discovers its main window."""
    try:
        win = desktop_service.launch_application(request.executable_name, request.arguments)
        return win
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/windows", response_model=list[WindowInfo])
async def list_windows(include_invisible: bool = Query(default=False)) -> list[WindowInfo]:
    """Lists discovered top-level windows on the interactive desktop."""
    try:
        return desktop_service.list_windows(include_invisible=include_invisible)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/windows/{window_ref}", response_model=WindowInfo)
async def get_window(window_ref: str) -> WindowInfo:
    """Retrieves verified metadata for a specific window reference."""
    try:
        win = desktop_service.get_window(window_ref)
        if not win:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Window not found or stale")
        return win
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/windows/{window_ref}/manage")
async def manage_window(window_ref: str, req: WindowManageRequest) -> dict[str, Any]:
    """Changes window state (activate, minimize, maximize, restore, close)."""
    try:
        success = await desktop_service.manage_window(window_ref, req.action)
        return {"window_ref": window_ref, "action": req.action.value, "success": success}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/windows/{window_ref}/inspect", response_model=UITreeSnapshot)
async def inspect_tree(
    window_ref: str,
    options: InspectionOptions | None = None,
) -> UITreeSnapshot:
    """Traverses and inspects the Microsoft UI Automation tree of an authorized window."""
    try:
        return await desktop_service.inspect_window_tree(window_ref, options)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/elements/search", response_model=list[UIElementInfo])
async def search_elements(req: ElementSearchRequest) -> list[UIElementInfo]:
    """Finds controls matching an ElementQuery within an authorized window."""
    try:
        return await desktop_service.find_elements(req.window_ref, req.query)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/actions", response_model=DesktopActionResult)
async def execute_action(req: DesktopActionRequest) -> DesktopActionResult:
    """Executes a typed desktop action with post-action verification."""
    try:
        return await desktop_service.execute_action(req)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/actions", response_model=list[DesktopActionResult])
@router.get("/history", response_model=list[DesktopActionResult])
async def list_actions(limit: int = Query(default=50, ge=1, le=200)) -> list[DesktopActionResult]:
    """Retrieves action execution history."""
    return desktop_service.get_action_history(limit=limit)


@router.get("/actions/{action_id}", response_model=DesktopActionResult)
async def get_action(action_id: str) -> DesktopActionResult:
    """Retrieves action execution record by ID."""
    act = desktop_service.get_action(action_id)
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    return act


@router.get("/tasks", response_model=list[DesktopTaskResponse])
async def list_tasks() -> list[DesktopTaskResponse]:
    """Lists submitted desktop tasks."""
    return desktop_service.list_tasks()


@router.post("/tasks", response_model=DesktopTaskResponse, status_code=status.HTTP_201_CREATED)
async def submit_task(req: DesktopTaskRequest) -> DesktopTaskResponse:
    """Submits a new desktop automation task."""
    try:
        return desktop_service.submit_task(req)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/tasks/{task_id}", response_model=DesktopTaskResponse)
async def get_task(task_id: str) -> DesktopTaskResponse:
    """Retrieves desktop task by ID."""
    task = desktop_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> dict[str, Any]:
    """Cancels a pending or running desktop task."""
    success = desktop_service.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {"task_id": task_id, "status": "cancelled"}


@router.get("/diagnostics", response_model=DesktopDiagnosticsInfo)
async def get_diagnostics() -> DesktopDiagnosticsInfo:
    """Collects comprehensive Windows desktop and COM worker diagnostics."""
    return desktop_service.get_diagnostics()


@router.get("/capabilities")
async def get_capabilities() -> list[dict[str, Any]]:
    """Lists registered desktop automation capabilities."""
    return [
        {"name": "desktop.list_applications", "description": "Discovers running desktop applications"},
        {"name": "desktop.list_windows", "description": "Enumerates top-level windows"},
        {"name": "desktop.inspect_window", "description": "Inspects window metadata"},
        {"name": "desktop.inspect_tree", "description": "Inspects UI Automation accessibility tree"},
        {"name": "desktop.find_elements", "description": "Finds accessible controls by locator"},
        {"name": "desktop.invoke", "description": "Invokes buttons and commands"},
        {"name": "desktop.set_value", "description": "Sets text into editable controls"},
        {"name": "desktop.toggle", "description": "Toggles checkboxes and switches"},
        {"name": "desktop.select", "description": "Selects list and tab items"},
        {"name": "desktop.scroll", "description": "Scrolls container elements"},
        {"name": "desktop.manage_window", "description": "Activates, minimizes, maximizes, or closes windows"},
        {"name": "desktop.press_key", "description": "Sends keystrokes to verified foreground window"},
    ]
