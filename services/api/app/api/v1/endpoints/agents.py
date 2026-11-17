"""FastAPI REST endpoints for Specialist and Coordination AI Agents (Stage 13)."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.db.engine import get_db_session
from app.orchestration.agents.contracts import (
    AgentCategory,
    AgentConfigurationUpdate,
    AgentManifest,
    AgentStatusResponse,
    AvailabilityState,
)
from app.orchestration.agents.registry import get_agent_registry
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.contracts import CapabilityDefinition
from app.repositories.workflow_repository import WorkflowRepository

logger = logging.getLogger("autonom.api.agents")

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=list[AgentManifest])
async def list_agents(
    category: str | None = Query(default=None, description="Filter by agent category"),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by availability state"),
    only_available: bool = Query(default=False, description="Filter only currently available agents"),
) -> list[AgentManifest]:
    """List all registered autonomous coordination and specialist execution agents."""
    reg = get_agent_registry()
    return reg.list_manifests(category=category, status=status_filter, only_available=only_available)


@router.get("/capabilities", response_model=list[CapabilityDefinition])
async def list_all_capabilities() -> list[CapabilityDefinition]:
    """List all registered capabilities across all specialist agents with input/output schemas."""
    return get_capability_registry().list_definitions()


@router.get("/{agent_id}", response_model=AgentManifest)
async def get_agent(agent_id: str) -> AgentManifest:
    """Retrieve full typed manifest and metadata for a specific agent."""
    manifest = get_agent_registry().get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")
    return manifest


@router.get("/{agent_id}/capabilities", response_model=list[CapabilityDefinition])
async def get_agent_capabilities(agent_id: str) -> list[CapabilityDefinition]:
    """List capabilities supported by a specific agent along with their schemas."""
    manifest = get_agent_registry().get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")

    cap_reg = get_capability_registry()
    definitions = []
    for cap_id in manifest.capabilities:
        handler = cap_reg.get(cap_id)
        if handler:
            definitions.append(handler.definition)
    return definitions


@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str) -> AgentStatusResponse:
    """Retrieve operational status, active assignment count, and execution summary."""
    try:
        return get_agent_registry().get_agent_status(agent_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")


@router.get("/{agent_id}/executions")
async def get_agent_executions(
    agent_id: str,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict[str, Any]]:
    """Retrieve execution trace history for this agent across all workflows."""
    manifest = get_agent_registry().get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")

    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        records = await repo.get_executions_for_agent(agent_id, limit=limit)
        return [
            {
                "id": r.id,
                "agent_id": r.agent_id,
                "workflow_id": r.workflow_id,
                "step_id": r.step_id,
                "status": r.status,
                "model_used": r.model_used,
                "tokens_used": r.tokens_used,
                "cost_usd": r.cost_usd,
                "duration_ms": r.duration_ms,
                "created_at": r.created_at.isoformat(),
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in records
        ]


@router.get("/{agent_id}/configuration")
async def get_agent_configuration(agent_id: str) -> dict[str, Any]:
    """Retrieve current configurable parameters for an agent."""
    manifest = get_agent_registry().get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")

    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        db_cfg = await repo.get_agent_configuration(agent_id)

    return {
        "agent_id": agent_id,
        "enabled": db_cfg.enabled if db_cfg else manifest.enabled,
        "preferred_model": db_cfg.preferred_model if db_cfg else manifest.model_profile.preferred_model,
        "concurrency_limit": db_cfg.concurrency_limit if db_cfg else manifest.execution_limits.concurrency_limit,
        "timeout_seconds": db_cfg.timeout_seconds if db_cfg else manifest.execution_limits.timeout_seconds,
        "temperature": db_cfg.temperature if db_cfg else manifest.model_profile.temperature,
        "max_tokens": db_cfg.max_tokens if db_cfg else manifest.model_profile.max_output_tokens,
        "local_first": db_cfg.local_first if db_cfg else manifest.model_profile.local_first,
        "cloud_permitted": db_cfg.cloud_permitted if db_cfg else manifest.model_profile.cloud_permitted,
        "allowed_capabilities": db_cfg.allowed_capabilities_json if (db_cfg and db_cfg.allowed_capabilities_json) else manifest.capabilities,
    }


@router.patch("/{agent_id}/configuration", response_model=AgentManifest)
async def update_agent_configuration(
    agent_id: str,
    update: AgentConfigurationUpdate,
) -> AgentManifest:
    """Update permitted configuration parameters for an agent."""
    reg = get_agent_registry()
    manifest = reg.get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")

    # Update in memory registry
    updated_manifest = reg.update_configuration(agent_id, update)

    # Persist in SQLite
    async with get_db_session() as session:
        repo = WorkflowRepository(session)
        await repo.save_agent_configuration(
            agent_id=agent_id,
            enabled=updated_manifest.enabled,
            preferred_model=updated_manifest.model_profile.preferred_model,
            concurrency_limit=updated_manifest.execution_limits.concurrency_limit,
            timeout_seconds=updated_manifest.execution_limits.timeout_seconds,
            temperature=updated_manifest.model_profile.temperature,
            max_tokens=updated_manifest.model_profile.max_output_tokens,
            local_first=updated_manifest.model_profile.local_first,
            cloud_permitted=updated_manifest.model_profile.cloud_permitted,
            allowed_capabilities=updated_manifest.capabilities,
        )

    return updated_manifest


@router.post("/{agent_id}/test")
async def test_agent(agent_id: str) -> dict[str, Any]:
    """Execute a safe, non-destructive diagnostic test on the agent."""
    try:
        return get_agent_registry().run_diagnostic_test(agent_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found")
