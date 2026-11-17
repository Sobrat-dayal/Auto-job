"""FastAPI endpoints for Multi-Agent Orchestration (Stage 12)."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.engine import get_db_session
from app.orchestration.agents.registry import get_agent_registry
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.contracts import (
    AgentDefinition,
    CapabilityDefinition,
    WorkflowCreateRequest,
    WorkflowReplanRequest,
    WorkflowResponse,
    WorkflowStatus,
    WorkflowSummary,
)
from app.orchestration.graph import DependencyGraph
from app.orchestration.supervisor import SupervisorAgent, get_supervisor_agent
from app.repositories.workflow_repository import WorkflowRepository

logger = logging.getLogger("autonom.api.orchestration")

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])


def get_supervisor() -> SupervisorAgent:
    return get_supervisor_agent()


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    request: WorkflowCreateRequest,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Create a new multi-agent workflow and generate its structured DAG execution plan."""
    try:
        return await supervisor.create_workflow(request)
    except Exception as exc:
        logger.error("Failed to create workflow: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {exc}",
        )


@router.get("/workflows", response_model=list[WorkflowSummary])
async def list_workflows(
    status_filter: WorkflowStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> list[WorkflowSummary]:
    """List all autonomous workflows with execution summaries."""
    return await supervisor.list_workflows(status=status_filter, limit=limit, offset=offset)


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Retrieve full details of a workflow including active plan and step statuses."""
    try:
        return await supervisor.get_workflow_status(workflow_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.post("/workflows/{workflow_id}/start", response_model=WorkflowResponse)
async def start_workflow(
    workflow_id: str,
    background: bool = Query(default=True),
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Trigger execution of an existing workflow plan."""
    try:
        return await supervisor.start_workflow(workflow_id, background=background)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/workflows/{workflow_id}/pause", response_model=WorkflowResponse)
async def pause_workflow(
    workflow_id: str,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Pause an active workflow execution run."""
    try:
        return await supervisor.pause_workflow(workflow_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.post("/workflows/{workflow_id}/resume", response_model=WorkflowResponse)
async def resume_workflow(
    workflow_id: str,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Resume a paused workflow run."""
    try:
        return await supervisor.resume_workflow(workflow_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.post("/workflows/{workflow_id}/cancel", response_model=WorkflowResponse)
async def cancel_workflow(
    workflow_id: str,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Cancel a running, queued, or planned workflow."""
    try:
        return await supervisor.cancel_workflow(workflow_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.post("/workflows/{workflow_id}/replan", response_model=WorkflowResponse)
async def replan_workflow(
    workflow_id: str,
    request: WorkflowReplanRequest,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> WorkflowResponse:
    """Dynamically revise an existing workflow plan (e.g. after step failures or constraint changes)."""
    try:
        return await supervisor.replan_workflow(workflow_id, request)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.get("/workflows/{workflow_id}/dag")
async def get_workflow_dag(
    workflow_id: str,
    supervisor: SupervisorAgent = Depends(get_supervisor),
) -> dict[str, Any]:
    """Retrieve DAG topological graph metadata for visual rendering in desktop UI."""
    try:
        wf = await supervisor.get_workflow_status(workflow_id)
        if not wf.active_plan:
            return {"steps": [], "stages": [], "topological_order": []}
        graph = DependencyGraph(wf.active_plan.steps)
        return graph.to_dict()
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.get("/workflows/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
) -> list[dict[str, Any]]:
    """Retrieve agent execution history for a workflow."""
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        executions = await repo.get_agent_executions(workflow_id)
        return [
            {
                "id": e.id,
                "step_id": e.step_id,
                "agent_id": e.agent_id,
                "capability_id": e.capability_id,
                "status": e.status,
                "execution_time_ms": e.execution_time_ms,
                "created_at": e.created_at.isoformat(),
            }
            for e in executions
        ]


@router.get("/workflows/{workflow_id}/messages")
async def get_workflow_messages(
    workflow_id: str,
) -> list[dict[str, Any]]:
    """Retrieve agent communication message log for a workflow."""
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        messages = await repo.get_agent_messages(workflow_id)
        return [
            {
                "id": m.id,
                "sender_agent_id": m.sender_agent_id,
                "recipient_agent_id": m.recipient_agent_id,
                "message_type": m.message_type,
                "step_id": m.step_id,
                "payload": m.payload,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]


@router.get("/workflows/{workflow_id}/verifications")
async def get_workflow_verifications(
    workflow_id: str,
) -> list[dict[str, Any]]:
    """Retrieve step verification audit results."""
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        verifications = await repo.get_verification_results(workflow_id)
        return [
            {
                "id": v.id,
                "step_id": v.step_id,
                "verification_type": v.verification_type,
                "status": v.status,
                "passed": v.passed,
                "score": v.score,
                "evidence": v.evidence,
                "details": v.details,
                "created_at": v.created_at.isoformat(),
            }
            for v in verifications
        ]


@router.get("/workflows/{workflow_id}/recoveries")
async def get_workflow_recoveries(
    workflow_id: str,
) -> list[dict[str, Any]]:
    """Retrieve recovery attempts and remediation records."""
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        recoveries = await repo.get_recovery_attempts(workflow_id)
        return [
            {
                "id": r.id,
                "step_id": r.step_id,
                "attempt_number": r.attempt_number,
                "failure_category": r.failure_category,
                "action_taken": r.action_taken,
                "reason": r.reason,
                "resolved": r.resolved,
                "created_at": r.created_at.isoformat(),
            }
            for r in recoveries
        ]


@router.get("/agents", response_model=list[AgentDefinition])
async def list_agents(
    only_available: bool = Query(default=False),
) -> list[AgentDefinition]:
    """List all registered autonomous coordination and specialist execution agents."""
    return get_agent_registry().list_agents(only_available=only_available)


@router.get("/capabilities", response_model=list[CapabilityDefinition])
async def list_capabilities() -> list[CapabilityDefinition]:
    """List all registered capabilities and their input/output schemas."""
    return get_capability_registry().list_definitions()


@router.get("/stats")
async def get_orchestration_stats() -> dict[str, Any]:
    """Retrieve global workflow execution metrics and status aggregates."""
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        return await repo.get_workflow_stats()
