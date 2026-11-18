"""Authenticated REST API endpoints for Stage 19 Hybrid Computer Interaction Engine."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.security import require_auth
from app.hybrid.contracts import (
    CapabilityProbe,
    HybridActionType,
    HybridDiagnosticsInfo,
    HybridTaskRequest,
    HybridTaskResponse,
    InteractionAction,
    InteractionMethod,
    InteractionObservation,
    InteractionResult,
    InteractionTarget,
    ObservationRequest,
    RoutingDecisionRecordSchema,
)
from app.hybrid.errors import (
    EmergencyStopActiveError,
    FallbackBlockedError,
    NoEligibleMethodError,
    NonIdempotentActionBlockedError,
    SessionLockedError,
    StaleTargetError,
)
from app.hybrid.service import HybridComputerService, hybrid_computer_service

logger = logging.getLogger("autonom.api.v1.hybrid")

router = APIRouter(prefix="/hybrid", tags=["hybrid"], dependencies=[Depends(require_auth)])


def get_service() -> HybridComputerService:
    return hybrid_computer_service


class ResolveTargetRequest(BaseModel):
    target_hint: Optional[str] = None
    session_id: Optional[str] = None
    dom_selector: Optional[str] = None
    window_title: Optional[str] = None
    window_handle: Optional[int] = None
    coordinates: Optional[dict[str, Any]] = None
    process_name: Optional[str] = None


class RoutePreviewRequest(BaseModel):
    target: InteractionTarget
    action_type: Optional[HybridActionType] = None
    preferred_method: Optional[InteractionMethod] = None


class KillswitchRequest(BaseModel):
    reason: str = Field(default="Operator hybrid killswitch activation")


@router.get("/status")
async def get_hybrid_status(
    service: HybridComputerService = Depends(get_service),
) -> dict[str, Any]:
    """Get operational status and method availability of the Hybrid Computer Interaction Engine."""
    return service.get_status()


@router.get("/methods", response_model=list[InteractionMethod])
async def list_methods(
    service: HybridComputerService = Depends(get_service),
) -> list[InteractionMethod]:
    """List all registered interaction methods (DOM, UIA, Win32, Visual)."""
    return service.list_methods()


@router.get("/capabilities")
async def get_capabilities(
    service: HybridComputerService = Depends(get_service),
) -> list[dict[str, Any]]:
    """Return capability and health telemetry for all interaction methods."""
    return service.get_capabilities()


@router.post("/targets/resolve", response_model=InteractionTarget)
async def resolve_target(
    request: ResolveTargetRequest,
    service: HybridComputerService = Depends(get_service),
) -> InteractionTarget:
    """Resolve partial target parameters into a normalized InteractionTarget."""
    return await service.resolve_target(
        target_hint=request.target_hint,
        session_id=request.session_id,
        dom_selector=request.dom_selector,
        window_title=request.window_title,
        window_handle=request.window_handle,
        coordinates=request.coordinates,
        process_name=request.process_name,
    )


@router.post("/methods/probe", response_model=dict[str, CapabilityProbe])
async def probe_methods(
    target: InteractionTarget,
    service: HybridComputerService = Depends(get_service),
) -> dict[str, CapabilityProbe]:
    """Probe all interaction adapters for availability and applicability against a target."""
    return await service.probe_methods(target)


@router.post("/route/preview", response_model=RoutingDecisionRecordSchema)
async def preview_route(
    request: RoutePreviewRequest,
    service: HybridComputerService = Depends(get_service),
) -> RoutingDecisionRecordSchema:
    """Simulate and explain method routing without executing any desktop/browser actions."""
    try:
        return await service.preview_route(
            target=request.target,
            action_type=request.action_type,
            preferred_method=request.preferred_method,
        )
    except NoEligibleMethodError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.post("/observe", response_model=InteractionObservation)
async def observe_target(
    request: ObservationRequest,
    service: HybridComputerService = Depends(get_service),
) -> InteractionObservation:
    """Capture normalized observations across DOM, UIA, or visual surfaces."""
    try:
        return await service.observe(request)
    except EmergencyStopActiveError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except SessionLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/actions", response_model=InteractionResult)
async def execute_action(
    action: InteractionAction,
    service: HybridComputerService = Depends(get_service),
) -> InteractionResult:
    """Execute a unified action with automatic routing, verification, and bounded fallback."""
    try:
        return await service.execute_action(action)
    except EmergencyStopActiveError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except SessionLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except StaleTargetError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except NoEligibleMethodError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except (FallbackBlockedError, NonIdempotentActionBlockedError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/actions/{action_id}", response_model=InteractionResult)
async def get_action(
    action_id: str,
    service: HybridComputerService = Depends(get_service),
) -> InteractionResult:
    """Retrieve result of a previous hybrid action."""
    action_res = service.get_action(action_id)
    if not action_res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action '{action_id}' not found",
        )
    return action_res


@router.get("/tasks", response_model=list[HybridTaskResponse])
async def list_tasks(
    limit: int = Query(default=50, ge=1, le=200),
    service: HybridComputerService = Depends(get_service),
) -> list[HybridTaskResponse]:
    """List recent hybrid computer execution tasks."""
    return service.list_tasks(limit=limit)


@router.post("/tasks", response_model=HybridTaskResponse)
async def submit_task(
    request: HybridTaskRequest,
    service: HybridComputerService = Depends(get_service),
) -> HybridTaskResponse:
    """Submit a hybrid computer execution task."""
    try:
        return await service.submit_task(request)
    except EmergencyStopActiveError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except SessionLockedError as exc:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/tasks/{task_id}", response_model=HybridTaskResponse)
async def get_task(
    task_id: str,
    service: HybridComputerService = Depends(get_service),
) -> HybridTaskResponse:
    """Retrieve hybrid task status and details by task ID."""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hybrid task '{task_id}' not found",
        )
    return task


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    service: HybridComputerService = Depends(get_service),
) -> dict[str, Any]:
    """Cancel a running hybrid task."""
    cancelled = service.cancel_task(task_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found or cannot be cancelled",
        )
    return {"task_id": task_id, "status": "cancelled"}


@router.get("/tasks/{task_id}/history")
async def get_task_history(
    task_id: str,
    service: HybridComputerService = Depends(get_service),
) -> dict[str, Any]:
    """Retrieve execution attempt history and fallback records for a task."""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hybrid task '{task_id}' not found",
        )
    return {
        "task_id": task.task_id,
        "attempts": task.attempts,
        "final_result": task.final_result.model_dump(mode="json") if task.final_result else None,
    }


@router.get("/tasks/{task_id}/routing", response_model=RoutingDecisionRecordSchema)
async def get_task_routing(
    task_id: str,
    service: HybridComputerService = Depends(get_service),
) -> RoutingDecisionRecordSchema:
    """Retrieve the explainable routing decision record for a task."""
    task = service.get_task(task_id)
    if not task or not task.routing_decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Routing decision for task '{task_id}' not found",
        )
    return task.routing_decision


@router.get("/diagnostics", response_model=HybridDiagnosticsInfo)
async def get_diagnostics(
    service: HybridComputerService = Depends(get_service),
) -> HybridDiagnosticsInfo:
    """Get consolidated diagnostics and health report for the Hybrid Engine."""
    return service.get_diagnostics()


@router.post("/killswitch/activate")
async def activate_killswitch(
    request: KillswitchRequest,
    service: HybridComputerService = Depends(get_service),
) -> dict[str, Any]:
    """Trigger the hybrid killswitch and global emergency stop."""
    await service.activate_killswitch(reason=request.reason)
    return {"status": "activated", "reason": request.reason}


@router.post("/killswitch/deactivate")
async def deactivate_killswitch(
    service: HybridComputerService = Depends(get_service),
) -> dict[str, Any]:
    """Deactivate the hybrid killswitch and reset global emergency stop."""
    await service.deactivate_killswitch()
    return {"status": "deactivated"}
