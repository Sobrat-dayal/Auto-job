"""Repository for managing authorization policies, grants, approval requests, decisions, and emergency stop."""

from datetime import UTC, datetime
import logging
from typing import Any
import uuid

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalRequestRecord,
    AuthorizationDecisionRecord,
    AuthorizationGrantRecord,
    AuthorizationPolicyRecord,
    AuthorizationPolicyVersionRecord,
    EmergencyStopStateRecord,
)

logger = logging.getLogger("autonom.security.authorization_repository")


class AuthorizationRepository:
    """Manages transactional persistence for policies, grants, approvals, and emergency stop."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --------------------------------------------------------------------------
    # 1. Emergency Stop & Pause State
    # --------------------------------------------------------------------------
    async def get_emergency_stop_state(self) -> EmergencyStopStateRecord:
        """Retrieves singleton emergency stop and automation pause state, creating default if missing."""
        result = await self.session.execute(
            select(EmergencyStopStateRecord).where(EmergencyStopStateRecord.id == "global_state")
        )
        record = result.scalar_one_or_none()
        if not record:
            record = EmergencyStopStateRecord(
                id="global_state",
                is_emergency_stop_active=False,
                is_automation_paused=False,
                updated_at=datetime.now(UTC),
            )
            self.session.add(record)
            await self.session.commit()
            await self.session.refresh(record)
        return record

    async def set_emergency_stop(
        self,
        active: bool,
        activated_by: str = "user",
        reason: str | None = None,
    ) -> EmergencyStopStateRecord:
        """Atomically toggles global emergency stop state."""
        state = await self.get_emergency_stop_state()
        state.is_emergency_stop_active = active
        now = datetime.now(UTC)
        if active:
            state.emergency_stop_activated_at = now
            state.emergency_stop_activated_by = activated_by
            state.emergency_stop_reason = reason
        else:
            state.emergency_stop_reason = None
        state.updated_at = now
        await self.session.commit()
        await self.session.refresh(state)
        return state

    async def set_automation_pause(
        self,
        paused: bool,
        paused_by: str = "user",
        reason: str | None = None,
    ) -> EmergencyStopStateRecord:
        """Atomically toggles background automation dispatch pause state."""
        state = await self.get_emergency_stop_state()
        state.is_automation_paused = paused
        now = datetime.now(UTC)
        if paused:
            state.automation_paused_at = now
            state.automation_paused_by = paused_by
            state.automation_pause_reason = reason
        else:
            state.automation_pause_reason = None
        state.updated_at = now
        await self.session.commit()
        await self.session.refresh(state)
        return state

    # --------------------------------------------------------------------------
    # 2. Authorization Policies
    # --------------------------------------------------------------------------
    async def list_policies(self, enabled_only: bool = False) -> list[AuthorizationPolicyRecord]:
        """Lists authorization policies ordered by creation."""
        query = select(AuthorizationPolicyRecord)
        if enabled_only:
            query = query.where(AuthorizationPolicyRecord.is_enabled.is_(True))
        query = query.order_by(AuthorizationPolicyRecord.id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_policy(self, policy_id: str) -> AuthorizationPolicyRecord | None:
        """Fetches a single policy by ID."""
        result = await self.session.execute(
            select(AuthorizationPolicyRecord).where(AuthorizationPolicyRecord.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def create_policy(self, record: AuthorizationPolicyRecord) -> AuthorizationPolicyRecord:
        """Creates a new authorization policy and saves initial version."""
        self.session.add(record)
        version_snapshot = AuthorizationPolicyVersionRecord(
            policy_id=record.id,
            version=record.version,
            policy_snapshot_json={
                "id": record.id,
                "name": record.name,
                "description": record.description,
                "is_enabled": record.is_enabled,
                "is_system": record.is_system,
                "subject_scope": record.subject_scope,
                "category_scope": record.category_scope,
                "action_scope_json": record.action_scope_json,
                "resource_scope_json": record.resource_scope_json,
                "effect": record.effect,
                "conditions_json": record.conditions_json,
            },
            modified_by="user",
            change_reason="Initial creation",
            created_at=datetime.now(UTC),
        )
        self.session.add(version_snapshot)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def update_policy(
        self,
        policy_id: str,
        update_data: dict[str, Any],
        expected_version: int | None = None,
        modified_by: str = "user",
        change_reason: str | None = None,
    ) -> AuthorizationPolicyRecord:
        """Updates policy with optimistic concurrency version check."""
        policy = await self.get_policy(policy_id)
        if not policy:
            raise KeyError(f"Policy '{policy_id}' not found")

        if expected_version is not None and policy.version != expected_version:
            raise ValueError(
                f"Version conflict for policy '{policy_id}': expected {expected_version}, found {policy.version}"
            )

        for key, value in update_data.items():
            if hasattr(policy, key) and key not in ("id", "version", "created_at"):
                setattr(policy, key, value)

        policy.version += 1
        policy.updated_at = datetime.now(UTC)

        version_snapshot = AuthorizationPolicyVersionRecord(
            policy_id=policy.id,
            version=policy.version,
            policy_snapshot_json={
                "id": policy.id,
                "name": policy.name,
                "description": policy.description,
                "is_enabled": policy.is_enabled,
                "is_system": policy.is_system,
                "subject_scope": policy.subject_scope,
                "category_scope": policy.category_scope,
                "action_scope_json": policy.action_scope_json,
                "resource_scope_json": policy.resource_scope_json,
                "effect": policy.effect,
                "conditions_json": policy.conditions_json,
            },
            modified_by=modified_by,
            change_reason=change_reason or "Policy update",
            created_at=datetime.now(UTC),
        )
        self.session.add(version_snapshot)
        await self.session.commit()
        await self.session.refresh(policy)
        return policy

    async def get_policy_versions(self, policy_id: str) -> list[AuthorizationPolicyVersionRecord]:
        """Lists historical snapshots for a policy."""
        result = await self.session.execute(
            select(AuthorizationPolicyVersionRecord)
            .where(AuthorizationPolicyVersionRecord.policy_id == policy_id)
            .order_by(desc(AuthorizationPolicyVersionRecord.version))
        )
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # 3. Authorization Grants (Preauthorized Autonomy)
    # --------------------------------------------------------------------------
    async def list_grants(
        self,
        active_only: bool = False,
        subject_id: str | None = None,
        workflow_id: str | None = None,
    ) -> list[AuthorizationGrantRecord]:
        """Lists authorization grants with optional filters."""
        query = select(AuthorizationGrantRecord)
        if active_only:
            now = datetime.now(UTC)
            query = query.where(
                AuthorizationGrantRecord.is_revoked.is_(False),
                (AuthorizationGrantRecord.valid_until.is_(None)) | (AuthorizationGrantRecord.valid_until > now),
            )
        if subject_id:
            query = query.where(
                (AuthorizationGrantRecord.subject_id == subject_id) | (AuthorizationGrantRecord.subject_id == "*")
            )
        if workflow_id:
            query = query.where(
                (AuthorizationGrantRecord.workflow_id == workflow_id) | (AuthorizationGrantRecord.workflow_id.is_(None))
            )
        query = query.order_by(desc(AuthorizationGrantRecord.created_at))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_grant(self, grant_id: str) -> AuthorizationGrantRecord | None:
        """Retrieves a single grant by ID."""
        result = await self.session.execute(
            select(AuthorizationGrantRecord).where(AuthorizationGrantRecord.id == grant_id)
        )
        return result.scalar_one_or_none()

    async def create_grant(self, grant: AuthorizationGrantRecord) -> AuthorizationGrantRecord:
        """Saves a new authorization grant."""
        self.session.add(grant)
        await self.session.commit()
        await self.session.refresh(grant)
        return grant

    async def revoke_grant(
        self,
        grant_id: str,
        reason: str | None = None,
        revoked_by: str = "user",
    ) -> AuthorizationGrantRecord:
        """Revokes an authorization grant."""
        grant = await self.get_grant(grant_id)
        if not grant:
            raise KeyError(f"Grant '{grant_id}' not found")
        grant.is_revoked = True
        grant.revoked_at = datetime.now(UTC)
        grant.revocation_reason = reason or f"Revoked by {revoked_by}"
        await self.session.commit()
        await self.session.refresh(grant)
        return grant

    async def increment_grant_use(self, grant_id: str) -> AuthorizationGrantRecord | None:
        """Increments use count on a grant."""
        grant = await self.get_grant(grant_id)
        if grant:
            grant.use_count += 1
            await self.session.commit()
            await self.session.refresh(grant)
        return grant

    # --------------------------------------------------------------------------
    # 4. Approval Requests
    # --------------------------------------------------------------------------
    async def create_approval_request(self, request: ApprovalRequestRecord) -> ApprovalRequestRecord:
        """Persists a new approval request in the queue."""
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_approval_request(self, approval_id: str) -> ApprovalRequestRecord | None:
        """Retrieves an approval request by ID."""
        result = await self.session.execute(
            select(ApprovalRequestRecord).where(ApprovalRequestRecord.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def find_pending_approval_by_digest(
        self,
        parameters_digest: str,
        workflow_id: str | None = None,
        step_id: str | None = None,
    ) -> ApprovalRequestRecord | None:
        """Finds existing pending approval with matching parameters digest for deduplication."""
        query = select(ApprovalRequestRecord).where(
            ApprovalRequestRecord.parameters_digest == parameters_digest,
            ApprovalRequestRecord.status == "pending",
        )
        if workflow_id:
            query = query.where(ApprovalRequestRecord.workflow_id == workflow_id)
        if step_id:
            query = query.where(ApprovalRequestRecord.step_id == step_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def find_approved_approval_by_digest(
        self,
        parameters_digest: str,
        workflow_id: str | None = None,
        step_id: str | None = None,
    ) -> ApprovalRequestRecord | None:
        """Finds existing approved (unconsumed) approval with matching parameters digest."""
        query = select(ApprovalRequestRecord).where(
            ApprovalRequestRecord.parameters_digest == parameters_digest,
            ApprovalRequestRecord.status == "approved",
        )
        if workflow_id:
            query = query.where(ApprovalRequestRecord.workflow_id == workflow_id)
        if step_id:
            query = query.where(ApprovalRequestRecord.step_id == step_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_approval_requests(
        self,
        status: str | None = None,
        workflow_id: str | None = None,
        agent_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ApprovalRequestRecord]:
        """Lists approval requests with filtering and pagination."""
        query = select(ApprovalRequestRecord)
        if status:
            query = query.where(ApprovalRequestRecord.status == status)
        if workflow_id:
            query = query.where(ApprovalRequestRecord.workflow_id == workflow_id)
        if agent_id:
            query = query.where(ApprovalRequestRecord.agent_id == agent_id)
        query = query.order_by(desc(ApprovalRequestRecord.requested_at)).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_approval_status(
        self,
        approval_id: str,
        status: str,
        decided_by: str | None = None,
        decision_reason: str | None = None,
    ) -> ApprovalRequestRecord:
        """Transitions approval state (approved, denied, expired, cancelled, revoked)."""
        appr = await self.get_approval_request(approval_id)
        if not appr:
            raise KeyError(f"Approval request '{approval_id}' not found")
        appr.status = status
        now = datetime.now(UTC)
        appr.decided_at = now
        appr.decided_by = decided_by or "user"
        appr.decision_reason = decision_reason
        await self.session.commit()
        await self.session.refresh(appr)
        return appr

    async def consume_approval(self, approval_id: str) -> ApprovalRequestRecord:
        """Marks an approved request as consumed (single-use replay prevention)."""
        appr = await self.get_approval_request(approval_id)
        if not appr:
            raise KeyError(f"Approval request '{approval_id}' not found")
        if appr.status != "approved":
            raise ValueError(f"Cannot consume approval with status '{appr.status}'")
        appr.status = "consumed"
        appr.consumed_at = datetime.now(UTC)
        await self.session.commit()
        await self.session.refresh(appr)
        return appr

    async def expire_stale_approvals(self) -> int:
        """Sweeps and marks expired pending approvals."""
        now = datetime.now(UTC)
        result = await self.session.execute(
            select(ApprovalRequestRecord).where(
                ApprovalRequestRecord.status == "pending",
                ApprovalRequestRecord.expires_at.is_not(None),
                ApprovalRequestRecord.expires_at <= now,
            )
        )
        expired = list(result.scalars().all())
        for req in expired:
            req.status = "expired"
            req.decided_at = now
            req.decision_reason = "Automatically expired by deadline"
        if expired:
            await self.session.commit()
        return len(expired)

    # --------------------------------------------------------------------------
    # 5. Decisions & Audit Logs
    # --------------------------------------------------------------------------
    async def record_decision(self, decision: AuthorizationDecisionRecord) -> AuthorizationDecisionRecord:
        """Records an authorization evaluation decision to the audit ledger."""
        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def list_decisions(
        self,
        limit: int = 50,
        offset: int = 0,
        correlation_id: str | None = None,
        outcome: str | None = None,
        agent_id: str | None = None,
    ) -> list[AuthorizationDecisionRecord]:
        """Queries authorization decision audit records."""
        query = select(AuthorizationDecisionRecord)
        if correlation_id:
            query = query.where(AuthorizationDecisionRecord.correlation_id == correlation_id)
        if outcome:
            query = query.where(AuthorizationDecisionRecord.outcome == outcome)
        if agent_id:
            query = query.where(AuthorizationDecisionRecord.agent_id == agent_id)
        query = query.order_by(desc(AuthorizationDecisionRecord.timestamp)).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
