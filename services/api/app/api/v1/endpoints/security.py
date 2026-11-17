"""FastAPI REST endpoints for the Central Authorization Engine, Policies, Grants, Approvals & Emergency Stop (Stage 14)."""

from datetime import UTC, datetime, timedelta
import logging
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.db.models import AuthorizationGrantRecord, AuthorizationPolicyRecord
from app.repositories.authorization_repository import AuthorizationRepository
from app.security.authorization.approvals import get_approval_manager
from app.security.authorization.contracts import (
    ActionEffect,
    ActorContext,
    ApprovalDecisionInput,
    ApprovalMode,
    ApprovalRequest,
    ApprovalStatus,
    AuthorizationDecision,
    AuthorizationRequest,
    EmergencyStopState,
    GrantDefinition,
    GrantType,
    PermissionCategory,
    PolicyDefinition,
    RiskLevel,
)
from app.security.authorization.emergency import get_emergency_stop_controller
from app.security.authorization.engine import get_authorization_engine

logger = logging.getLogger("autonom.api.v1.security")
router = APIRouter(prefix="/security", tags=["Security & Authorization"])


# --- Schemas ---
class PolicyCreateInput(BaseModel):
    id: Optional[str] = None
    name: str
    description: str = ""
    subject_scope: str = "*"
    category_scope: str = "*"
    action_scope: list[str] = Field(default_factory=list)
    resource_scope: dict[str, Any] = Field(default_factory=dict)
    effect: ActionEffect = ActionEffect.ALLOW
    conditions: dict[str, Any] = Field(default_factory=dict)


class PolicyUpdateInput(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    subject_scope: Optional[str] = None
    category_scope: Optional[str] = None
    action_scope: Optional[list[str]] = None
    resource_scope: Optional[dict[str, Any]] = None
    effect: Optional[ActionEffect] = None
    conditions: Optional[dict[str, Any]] = None
    expected_version: Optional[int] = None
    change_reason: Optional[str] = None


class GrantCreateInput(BaseModel):
    name: str
    grant_type: GrantType = GrantType.STANDING
    subject_type: str = "agent"
    subject_id: str = "*"
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    allowed_capabilities: list[str] = Field(default_factory=list)
    resource_scope: dict[str, Any] = Field(default_factory=dict)
    risk_limit: RiskLevel = RiskLevel.MODERATE
    valid_until_seconds: Optional[int] = None
    max_uses: Optional[int] = None


class EmergencyStopInput(BaseModel):
    reason: Optional[str] = None


# --- Endpoints ---

# 1. Permissions Taxonomy
@router.get("/permissions")
async def list_permissions(auth: AuthDep) -> dict[str, Any]:
    """Returns the centralized permission taxonomy and category definitions."""
    return {
        "categories": [c.value for c in PermissionCategory],
        "risk_levels": [r.value for r in RiskLevel],
        "action_effects": [e.value for e in ActionEffect],
        "approval_modes": [m.value for m in ApprovalMode],
        "grant_types": [g.value for g in GrantType],
    }


# 2. Emergency Stop & Automation Pause
@router.get("/emergency-stop", response_model=EmergencyStopState)
async def get_emergency_stop_status(auth: AuthDep) -> EmergencyStopState:
    """Returns authoritative global emergency stop and automation pause telemetry."""
    controller = get_emergency_stop_controller()
    return controller.get_state()


@router.post("/emergency-stop", response_model=EmergencyStopState)
async def activate_emergency_stop(
    body: EmergencyStopInput = EmergencyStopInput(),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> EmergencyStopState:
    """Immediately activates global Emergency Stop, blocking all autonomous and privileged operations."""
    controller = get_emergency_stop_controller()
    return await controller.activate_emergency_stop(activated_by=auth.client_id, reason=body.reason)


@router.post("/emergency-stop/clear", response_model=EmergencyStopState)
async def clear_emergency_stop(
    auth: AuthDep,
) -> EmergencyStopState:
    """Clears global Emergency Stop upon explicit human confirmation."""
    controller = get_emergency_stop_controller()
    return await controller.clear_emergency_stop(cleared_by=auth.client_id)


@router.post("/automation/pause", response_model=EmergencyStopState)
async def pause_automation(
    body: EmergencyStopInput = EmergencyStopInput(),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> EmergencyStopState:
    """Pauses background autonomous task and workflow dispatching."""
    controller = get_emergency_stop_controller()
    return await controller.pause_automation(paused_by=auth.client_id, reason=body.reason)


@router.post("/automation/resume", response_model=EmergencyStopState)
async def resume_automation(
    auth: AuthDep,
) -> EmergencyStopState:
    """Resumes background autonomous task and workflow dispatching."""
    controller = get_emergency_stop_controller()
    return await controller.resume_automation(resumed_by=auth.client_id)


# 3. Policies
@router.get("/policies")
async def list_policies(
    enabled_only: bool = Query(default=False),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> list[PolicyDefinition]:
    """Lists all active and configured authorization policies."""
    engine = get_authorization_engine()
    # Default baseline policies
    all_policies = await engine._load_all_policies()
    if enabled_only:
        all_policies = [p for p in all_policies if p.is_enabled]
    return all_policies


@router.post("/policies", response_model=PolicyDefinition, status_code=status.HTTP_201_CREATED)
async def create_policy(
    body: PolicyCreateInput,
    auth: AuthDep,
) -> PolicyDefinition:
    """Creates a new user authorization policy."""
    policy_id = body.id or f"pol_{uuid.uuid4().hex[:10]}"
    now = datetime.now(UTC)

    record = AuthorizationPolicyRecord(
        id=policy_id,
        name=body.name,
        description=body.description,
        version=1,
        is_enabled=True,
        is_system=False,
        subject_scope=body.subject_scope,
        category_scope=body.category_scope,
        action_scope_json=body.action_scope,
        resource_scope_json=body.resource_scope,
        effect=body.effect.value,
        conditions_json=body.conditions,
        created_at=now,
        updated_at=now,
    )

    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        created = await repo.create_policy(record)
        return PolicyDefinition(
            id=created.id,
            name=created.name,
            description=created.description,
            version=created.version,
            is_enabled=created.is_enabled,
            is_system=created.is_system,
            subject_scope=created.subject_scope,
            category_scope=created.category_scope,
            action_scope=created.action_scope_json,
            resource_scope=created.resource_scope_json,
            effect=ActionEffect(created.effect),
            conditions=created.conditions_json,
        )


@router.get("/policies/{id}", response_model=PolicyDefinition)
async def get_policy(id: str, auth: AuthDep) -> PolicyDefinition:
    """Retrieves policy details by ID."""
    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        record = await repo.get_policy(id)
        if not record:
            # Check default baseline policies
            engine = get_authorization_engine()
            for p in engine._default_policies:
                if p.id == id:
                    return p
            raise HTTPException(status_code=404, detail=f"Policy '{id}' not found")

        return PolicyDefinition(
            id=record.id,
            name=record.name,
            description=record.description,
            version=record.version,
            is_enabled=record.is_enabled,
            is_system=record.is_system,
            subject_scope=record.subject_scope,
            category_scope=record.category_scope,
            action_scope=record.action_scope_json,
            resource_scope=record.resource_scope_json,
            effect=ActionEffect(record.effect),
            conditions=record.conditions_json,
        )


@router.patch("/policies/{id}", response_model=PolicyDefinition)
async def update_policy(
    id: str,
    body: PolicyUpdateInput,
    auth: AuthDep,
) -> PolicyDefinition:
    """Updates an authorization policy with optimistic concurrency version check."""
    update_dict = body.model_dump(exclude_unset=True, exclude={"expected_version", "change_reason"})
    if "effect" in update_dict and update_dict["effect"] is not None:
        update_dict["effect"] = update_dict["effect"].value

    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        try:
            updated = await repo.update_policy(
                policy_id=id,
                update_data=update_dict,
                expected_version=body.expected_version,
                modified_by=auth.client_id,
                change_reason=body.change_reason,
            )
            return PolicyDefinition(
                id=updated.id,
                name=updated.name,
                description=updated.description,
                version=updated.version,
                is_enabled=updated.is_enabled,
                is_system=updated.is_system,
                subject_scope=updated.subject_scope,
                category_scope=updated.category_scope,
                action_scope=updated.action_scope_json,
                resource_scope=updated.resource_scope_json,
                effect=ActionEffect(updated.effect),
                conditions=updated.conditions_json,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Policy '{id}' not found")
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))


@router.post("/policies/{id}/revoke", response_model=PolicyDefinition)
async def revoke_policy(id: str, auth: AuthDep) -> PolicyDefinition:
    """Disables an authorization policy."""
    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        try:
            updated = await repo.update_policy(
                policy_id=id,
                update_data={"is_enabled": False},
                modified_by=auth.client_id,
                change_reason="Policy revoked by user",
            )
            return PolicyDefinition(
                id=updated.id,
                name=updated.name,
                description=updated.description,
                version=updated.version,
                is_enabled=updated.is_enabled,
                is_system=updated.is_system,
                subject_scope=updated.subject_scope,
                category_scope=updated.category_scope,
                action_scope=updated.action_scope_json,
                resource_scope=updated.resource_scope_json,
                effect=ActionEffect(updated.effect),
                conditions=updated.conditions_json,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Policy '{id}' not found")


@router.post("/policies/evaluate", response_model=AuthorizationDecision)
async def evaluate_policy_preview(
    request: AuthorizationRequest,
    auth: AuthDep,
) -> AuthorizationDecision:
    """Previews an authorization decision without executing the action."""
    engine = get_authorization_engine()
    return await engine.evaluate(request)


# 4. Grants (Preauthorized Autonomy)
@router.get("/grants", response_model=list[GrantDefinition])
async def list_grants(
    active_only: bool = Query(default=False),
    subject_id: Optional[str] = Query(default=None),
    workflow_id: Optional[str] = Query(default=None),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> list[GrantDefinition]:
    """Lists preauthorized autonomy grants."""
    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        records = await repo.list_grants(
            active_only=active_only,
            subject_id=subject_id,
            workflow_id=workflow_id,
        )
        return [
            GrantDefinition(
                id=r.id,
                name=r.name,
                grant_type=GrantType(r.grant_type),
                subject_type=r.subject_type,
                subject_id=r.subject_id,
                workflow_id=r.workflow_id,
                task_id=r.task_id,
                allowed_capabilities=r.allowed_capabilities_json or [],
                resource_scope=r.resource_scope_json or {},
                risk_limit=RiskLevel(r.risk_limit),
                valid_from=r.valid_from,
                valid_until=r.valid_until,
                max_uses=r.max_uses,
                use_count=r.use_count,
                is_revoked=r.is_revoked,
                revoked_at=r.revoked_at,
                revocation_reason=r.revocation_reason,
                created_by=r.created_by,
                created_at=r.created_at,
            )
            for r in records
        ]


@router.post("/grants", response_model=GrantDefinition, status_code=status.HTTP_201_CREATED)
async def create_grant(
    body: GrantCreateInput,
    auth: AuthDep,
) -> GrantDefinition:
    """Creates a new preauthorized autonomy grant."""
    now = datetime.now(UTC)
    valid_until = now + timedelta(seconds=body.valid_until_seconds) if body.valid_until_seconds else None

    record = AuthorizationGrantRecord(
        id=f"grant_{uuid.uuid4().hex[:10]}",
        name=body.name,
        grant_type=body.grant_type.value,
        subject_type=body.subject_type,
        subject_id=body.subject_id,
        workflow_id=body.workflow_id,
        task_id=body.task_id,
        allowed_capabilities_json=body.allowed_capabilities,
        resource_scope_json=body.resource_scope,
        risk_limit=body.risk_limit.value,
        valid_from=now,
        valid_until=valid_until,
        max_uses=body.max_uses,
        use_count=0,
        is_revoked=False,
        created_by=auth.client_id,
        created_at=now,
    )

    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        created = await repo.create_grant(record)
        return GrantDefinition(
            id=created.id,
            name=created.name,
            grant_type=GrantType(created.grant_type),
            subject_type=created.subject_type,
            subject_id=created.subject_id,
            workflow_id=created.workflow_id,
            task_id=created.task_id,
            allowed_capabilities=created.allowed_capabilities_json or [],
            resource_scope=created.resource_scope_json or {},
            risk_limit=RiskLevel(created.risk_limit),
            valid_from=created.valid_from,
            valid_until=created.valid_until,
            max_uses=created.max_uses,
            use_count=created.use_count,
            is_revoked=created.is_revoked,
            created_by=created.created_by,
            created_at=created.created_at,
        )


@router.post("/grants/{id}/revoke", response_model=GrantDefinition)
async def revoke_grant(
    id: str,
    reason: Optional[str] = Query(default=None),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> GrantDefinition:
    """Revokes a preauthorized autonomy grant."""
    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        try:
            revoked = await repo.revoke_grant(grant_id=id, reason=reason, revoked_by=auth.client_id)
            return GrantDefinition(
                id=revoked.id,
                name=revoked.name,
                grant_type=GrantType(revoked.grant_type),
                subject_type=revoked.subject_type,
                subject_id=revoked.subject_id,
                workflow_id=revoked.workflow_id,
                task_id=revoked.task_id,
                allowed_capabilities=revoked.allowed_capabilities_json or [],
                resource_scope=revoked.resource_scope_json or {},
                risk_limit=RiskLevel(revoked.risk_limit),
                valid_from=revoked.valid_from,
                valid_until=revoked.valid_until,
                max_uses=revoked.max_uses,
                use_count=revoked.use_count,
                is_revoked=revoked.is_revoked,
                revoked_at=revoked.revoked_at,
                revocation_reason=revoked.revocation_reason,
                created_by=revoked.created_by,
                created_at=revoked.created_at,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Grant '{id}' not found")


# 5. Approvals Queue
@router.get("/approvals", response_model=list[ApprovalRequest])
async def list_approvals(
    status: Optional[str] = Query(default=None),
    workflow_id: Optional[str] = Query(default=None),
    agent_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> list[ApprovalRequest]:
    """Lists approval requests from the queue."""
    manager = get_approval_manager()
    return await manager.list_requests(
        status=status,
        workflow_id=workflow_id,
        agent_id=agent_id,
        limit=limit,
        offset=offset,
    )


@router.get("/approvals/{id}", response_model=ApprovalRequest)
async def get_approval(id: str, auth: AuthDep) -> ApprovalRequest:
    """Retrieves full details of an approval request."""
    manager = get_approval_manager()
    request = await manager.get_request(id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Approval request '{id}' not found")
    return request


@router.post("/approvals/{id}/approve", response_model=ApprovalRequest)
async def approve_request(
    id: str,
    body: ApprovalDecisionInput = ApprovalDecisionInput(decision="approve"),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> ApprovalRequest:
    """Grants human approval for a pending request."""
    manager = get_approval_manager()
    try:
        return await manager.resolve_request(
            approval_id=id,
            decision="approve",
            decided_by=auth.client_id,
            reason=body.reason,
            approval_mode=body.approval_mode,
            valid_until_seconds=body.valid_until_seconds,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Approval request '{id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approvals/{id}/deny", response_model=ApprovalRequest)
async def deny_request(
    id: str,
    body: ApprovalDecisionInput = ApprovalDecisionInput(decision="deny"),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> ApprovalRequest:
    """Denies a pending approval request."""
    manager = get_approval_manager()
    try:
        return await manager.resolve_request(
            approval_id=id,
            decision="deny",
            decided_by=auth.client_id,
            reason=body.reason,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Approval request '{id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 6. Audit Logs
@router.get("/audit")
async def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    correlation_id: Optional[str] = Query(default=None),
    outcome: Optional[str] = Query(default=None),
    agent_id: Optional[str] = Query(default=None),
    auth: AuthDep = None,  # type: ignore[assignment]
) -> list[dict[str, Any]]:
    """Returns paginated authorization decision audit records."""
    async with get_db_session() as session:
        repo = AuthorizationRepository(session)
        records = await repo.list_decisions(
            limit=limit,
            offset=offset,
            correlation_id=correlation_id,
            outcome=outcome,
            agent_id=agent_id,
        )
        return [
            {
                "id": r.id,
                "correlation_id": r.correlation_id,
                "actor_id": r.actor_id,
                "agent_id": r.agent_id,
                "workflow_id": r.workflow_id,
                "step_id": r.step_id,
                "capability_id": r.capability_id,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "outcome": r.outcome,
                "policy_id": r.policy_id,
                "grant_id": r.grant_id,
                "reason_code": r.reason_code,
                "explanation": r.explanation,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in records
        ]
