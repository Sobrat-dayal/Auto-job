"""FastAPI REST endpoints for Visual Computer Automation (Stage 18)."""

from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.security import require_auth
from app.visual.contracts import (
    CaptureSessionCreateRequest,
    CaptureSessionResponse,
    DisplayInfo,
    OCRLine,
    OCRResult,
    Point2D,
    VisualActionRequest,
    VisualActionResult,
    VisualDiagnosticsInfo,
    VisualElementDetection,
    VisualGroundingResult,
    VisualTaskRequest,
    VisualTaskResponse,
)
from app.visual.service import visual_computer_service

router = APIRouter(prefix="/visual", tags=["visual"], dependencies=[Depends(require_auth)])


# Request body helpers
class FindTextRequest(BaseModel):
    query: str


class GroundRequest(BaseModel):
    query: str


class QuickClickRequest(BaseModel):
    session_id: str
    x: int
    y: int
    button: str = "left"
    clicks: int = 1


class QuickTypeRequest(BaseModel):
    session_id: str
    text: str
    target_element: Optional[str] = None


# -----------------------------------------------------------------------------
# Diagnostics & Monitors
# -----------------------------------------------------------------------------


@router.get("/diagnostics", response_model=VisualDiagnosticsInfo)
async def get_visual_diagnostics() -> VisualDiagnosticsInfo:
    """Returns visual engine diagnostics, hardware capture providers, and OCR status."""
    return visual_computer_service.get_diagnostics()


@router.get("/monitors", response_model=list[DisplayInfo])
async def list_monitors() -> list[DisplayInfo]:
    """Enumerates all active physical display monitors, resolutions, and DPI factors."""
    return visual_computer_service.list_monitors()


# -----------------------------------------------------------------------------
# Capture Sessions
# -----------------------------------------------------------------------------


@router.post("/sessions", response_model=CaptureSessionResponse)
async def create_capture_session(request: CaptureSessionCreateRequest) -> CaptureSessionResponse:
    """Creates a new screen or window capture session."""
    try:
        return await visual_computer_service.create_session(request)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions", response_model=list[CaptureSessionResponse])
async def list_capture_sessions() -> list[CaptureSessionResponse]:
    """Lists all active and idle capture sessions."""
    return visual_computer_service.list_sessions()


@router.get("/sessions/{session_id}", response_model=CaptureSessionResponse)
async def get_capture_session(session_id: str) -> CaptureSessionResponse:
    """Retrieves session details by session_id."""
    sess = visual_computer_service.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found")
    return sess


@router.delete("/sessions/{session_id}")
async def close_capture_session(session_id: str) -> dict[str, Any]:
    """Closes an active capture session and frees its frame buffers."""
    success = await visual_computer_service.close_session(session_id)
    return {"session_id": session_id, "closed": success}


@router.post("/sessions/{session_id}/frame")
async def capture_frame(session_id: str) -> dict[str, Any]:
    """Captures a new visual frame and returns metadata plus base64 thumbnail."""
    try:
        frame = await visual_computer_service.capture_frame(session_id)
        from app.visual.capture.preprocessing import FramePreprocessor

        b64 = FramePreprocessor.to_base64_png(frame.image)
        return {
            "frame_id": frame.frame_id,
            "session_id": session_id,
            "metadata": frame.metadata.model_dump(),
            "thumbnail_b64": b64,
        }
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# -----------------------------------------------------------------------------
# OCR & Visual Grounding
# -----------------------------------------------------------------------------


@router.post("/sessions/{session_id}/ocr", response_model=OCRResult)
async def run_ocr(session_id: str) -> OCRResult:
    """Runs offline Windows Media OCR on the latest session frame."""
    try:
        return await visual_computer_service.run_ocr(session_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/sessions/{session_id}/find-text", response_model=list[OCRLine])
async def find_text(session_id: str, req: FindTextRequest) -> list[OCRLine]:
    """Searches for text matching a query string in the session frame."""
    try:
        return await visual_computer_service.find_text(session_id, req.query)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/sessions/{session_id}/detect-elements", response_model=list[VisualElementDetection])
async def detect_elements(session_id: str) -> list[VisualElementDetection]:
    """Detects and categorizes interactive visual UI elements on screen."""
    try:
        return await visual_computer_service.detect_elements(session_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/sessions/{session_id}/ground", response_model=VisualGroundingResult)
async def ground_query(session_id: str, req: GroundRequest) -> VisualGroundingResult:
    """Grounds a natural language query into target desktop coordinates."""
    try:
        return await visual_computer_service.ground(session_id, req.query)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# -----------------------------------------------------------------------------
# Visual Actions Execution
# -----------------------------------------------------------------------------


@router.post("/sessions/{session_id}/actions", response_model=VisualActionResult)
async def execute_visual_action(session_id: str, req: VisualActionRequest) -> VisualActionResult:
    """Dispatches a coordinate-based or grounded action with post-action verification."""
    try:
        return await visual_computer_service.execute_action(session_id, req)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/quick-click", response_model=VisualActionResult)
async def quick_click(req: QuickClickRequest) -> VisualActionResult:
    """Executes an immediate mouse click at given desktop coordinates."""
    try:
        return await visual_computer_service.click(
            session_id=req.session_id,
            x=req.x,
            y=req.y,
            button=req.button,
            clicks=req.clicks,
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/quick-type", response_model=VisualActionResult)
async def quick_type(req: QuickTypeRequest) -> VisualActionResult:
    """Enters text into the focused or grounded control."""
    try:
        return await visual_computer_service.enter_text(
            session_id=req.session_id,
            text=req.text,
            query=req.target_element,
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# -----------------------------------------------------------------------------
# High-Level Visual Tasks
# -----------------------------------------------------------------------------


@router.post("/tasks", response_model=VisualTaskResponse)
async def execute_task(req: VisualTaskRequest) -> VisualTaskResponse:
    """Submits and executes an end-to-end visual computer task."""
    try:
        return await visual_computer_service.execute_task(req)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tasks", response_model=list[VisualTaskResponse])
async def list_tasks() -> list[VisualTaskResponse]:
    """Lists all tracked visual tasks."""
    return visual_computer_service.list_tasks()


@router.get("/tasks/{task_id}", response_model=VisualTaskResponse)
async def get_task(task_id: str) -> VisualTaskResponse:
    """Retrieves a specific visual task."""
    task = visual_computer_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found")
    return task


@router.get("/recovery-events")
async def list_recovery_events() -> list[dict[str, Any]]:
    """Returns the visual recovery history log."""
    return visual_computer_service.recovery_manager.history
