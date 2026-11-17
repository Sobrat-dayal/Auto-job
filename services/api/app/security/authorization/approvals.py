"""Approval Request Manager coordinating human-in-the-loop authorization gates and queue lifecycle."""

from datetime import UTC, datetime, timedelta
import logging
from typing import Optional
import uuid

from app.db.engine import get_db_session
from app.db.models import ApprovalRequestRecord, AuthorizationGrantRecord
from app.repositories.authorization_repository import AuthorizationRepository
from app.security.authorization.contracts import (
    ApprovalMode,
    ApprovalRequest,
    ApprovalStatus,
    AuthorizationRequest,
    GrantType,
    RiskLevel,
)

logger = logging.getLogger("autonom.security.approvals")


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


class ApprovalManager:
    """Manages creation, deduplication, resolution, and consumption of approval requests."""

    def __init__(self) -> None:
        pass

    async def create_or_get_request(
        self,
        auth_request: AuthorizationRequest,
        risk_level: RiskLevel,
        reason: str,
        approval_mode: ApprovalMode = ApprovalMode.ONE_TIME,
        expires_in_seconds: int = 3600,
    ) -> ApprovalRequest:
        """Finds existing pending approval for identical parameters or persists a new one."""
        digest = auth_request.compute_digest()

        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            existing = await repo.find_pending_approval_by_digest(
                parameters_digest=digest,
                workflow_id=auth_request.actor.workflow_id,
                step_id=auth_request.actor.step_id,
            )
            if existing:
                return self._to_contract(existing)

            now = datetime.now(UTC)
            expires_at = now + timedelta(seconds=expires_in_seconds) if expires_in_seconds else None

            # Redact any sensitive tokens before storing parameters
            safe_params = {
                k: v
                for k, v in auth_request.parameters.items()
                if not any(s in k.lower() for s in ("key", "secret", "token", "password", "vault"))
            }

            record = ApprovalRequestRecord(
                id=f"appr_{uuid.uuid4().hex[:10]}",
                workflow_id=auth_request.actor.workflow_id,
                task_id=auth_request.actor.task_id,
                step_id=auth_request.actor.step_id,
                agent_id=auth_request.actor.agent_id or "unknown",
                capability_id=auth_request.capability_id,
                action=auth_request.action,
                resource_type=auth_request.resource_type,
                resource_id=auth_request.resource_id,
                resource_scope_json=auth_request.resource_scope,
                parameters_digest=digest,
                parameters_json=safe_params,
                reason=reason or f"Action '{auth_request.action}' requires human authorization",
                risk_level=risk_level.value,
                status=ApprovalStatus.PENDING.value,
                approval_mode=approval_mode.value,
                requested_at=now,
                expires_at=expires_at,
            )
            created = await repo.create_approval_request(record)
            logger.info(
                "Created approval request '%s' for agent '%s' action '%s' (risk=%s)",
                created.id,
                created.agent_id,
                created.action,
                created.risk_level,
            )
            return self._to_contract(created)

    async def get_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Fetches an approval request by ID."""
        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            record = await repo.get_approval_request(approval_id)
            return self._to_contract(record) if record else None

    async def list_requests(
        self,
        status: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ApprovalRequest]:
        """Lists approval requests from the queue."""
        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            # Sweep expired
            await repo.expire_stale_approvals()
            records = await repo.list_approval_requests(
                status=status,
                workflow_id=workflow_id,
                agent_id=agent_id,
                limit=limit,
                offset=offset,
            )
            return [self._to_contract(r) for r in records]

    async def resolve_request(
        self,
        approval_id: str,
        decision: str,  # approve or deny
        decided_by: str = "user",
        reason: Optional[str] = None,
        approval_mode: ApprovalMode = ApprovalMode.ONE_TIME,
        valid_until_seconds: Optional[int] = None,
    ) -> ApprovalRequest:
        """Applies human decision (approve/deny) and optionally creates broader grant."""
        status = ApprovalStatus.APPROVED if decision.lower() == "approve" else ApprovalStatus.DENIED

        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            record = await repo.get_approval_request(approval_id)
            if not record:
                raise KeyError(f"Approval request '{approval_id}' not found")

            if record.status != ApprovalStatus.PENDING.value:
                raise ValueError(f"Approval request '{approval_id}' is already {record.status}")

            now = datetime.now(UTC)
            exp = _ensure_utc(record.expires_at)
            if exp and exp < now:
                await repo.update_approval_status(approval_id, ApprovalStatus.EXPIRED.value, decision_reason="Expired")
                raise ValueError(f"Approval request '{approval_id}' has expired")

            updated = await repo.update_approval_status(
                approval_id=approval_id,
                status=status.value,
                decided_by=decided_by,
                decision_reason=reason or f"Resolved as {status.value} by {decided_by}",
            )

            # If approved and mode is workflow_scoped or standing, generate corresponding grant
            if status == ApprovalStatus.APPROVED and approval_mode in (
                ApprovalMode.WORKFLOW_SCOPED,
                ApprovalMode.STANDING,
            ):
                valid_until = now + timedelta(seconds=valid_until_seconds) if valid_until_seconds else None
                grant_record = AuthorizationGrantRecord(
                    id=f"grant_{uuid.uuid4().hex[:10]}",
                    name=f"Grant for approval {approval_id}",
                    grant_type=(
                        GrantType.WORKFLOW_SCOPED.value
                        if approval_mode == ApprovalMode.WORKFLOW_SCOPED
                        else GrantType.STANDING.value
                    ),
                    subject_type="agent",
                    subject_id=record.agent_id,
                    workflow_id=record.workflow_id if approval_mode == ApprovalMode.WORKFLOW_SCOPED else None,
                    allowed_capabilities_json=[record.capability_id],
                    resource_scope_json=record.resource_scope_json,
                    risk_limit=record.risk_level,
                    valid_from=now,
                    valid_until=valid_until,
                    created_by=decided_by,
                    created_at=now,
                )
                await repo.create_grant(grant_record)
                logger.info(
                    "Generated %s grant '%s' from approved request '%s'",
                    grant_record.grant_type,
                    grant_record.id,
                    approval_id,
                )

            return self._to_contract(updated)

    async def consume_request(self, approval_id: str) -> None:
        """Marks an approved request as consumed to prevent replay attacks."""
        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            await repo.consume_approval(approval_id)
            logger.info("Approval request '%s' consumed (replay protected)", approval_id)

    def _to_contract(self, record: ApprovalRequestRecord) -> ApprovalRequest:
        return ApprovalRequest(
            id=record.id,
            workflow_id=record.workflow_id,
            task_id=record.task_id,
            step_id=record.step_id,
            agent_id=record.agent_id,
            capability_id=record.capability_id,
            action=record.action,
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            resource_scope=record.resource_scope_json or {},
            parameters_digest=record.parameters_digest,
            parameters=record.parameters_json or {},
            reason=record.reason,
            risk_level=RiskLevel(record.risk_level),
            status=ApprovalStatus(record.status),
            approval_mode=ApprovalMode(record.approval_mode),
            requested_at=_ensure_utc(record.requested_at) or datetime.now(UTC),
            expires_at=_ensure_utc(record.expires_at),
            decided_at=_ensure_utc(record.decided_at),
            decided_by=record.decided_by,
            decision_reason=record.decision_reason,
            consumed_at=_ensure_utc(record.consumed_at),
        )


_approval_manager: Optional[ApprovalManager] = None


def get_approval_manager() -> ApprovalManager:
    """Returns singleton ApprovalManager."""
    global _approval_manager
    if _approval_manager is None:
        _approval_manager = ApprovalManager()
    return _approval_manager
