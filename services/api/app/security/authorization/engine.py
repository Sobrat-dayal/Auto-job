"""Central Authorization Engine implementing deterministic policy evaluation, grants, and audit recording (Stage 14)."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Optional
import uuid

from app.db.engine import get_db_session
from app.db.models import AuthorizationDecisionRecord
from app.repositories.authorization_repository import AuthorizationRepository
from app.security.authorization.contracts import (
    ActionEffect,
    ApprovalStatus,
    AuthorizationDecision,
    AuthorizationRequest,
    GrantDefinition,
    PolicyDefinition,
    ReasonCode,
    RiskLevel,
)
from app.security.authorization.default_policies import get_default_policies
from app.security.authorization.emergency import get_emergency_stop_controller
from app.security.authorization.evaluator import (
    classify_action_risk,
    evaluate_grant_match,
    evaluate_policy_rule,
)

logger = logging.getLogger("autonom.security.authorization.engine")


class AuthorizationDeniedError(Exception):
    """Raised when an operation is denied by the Authorization Engine."""

    def __init__(self, decision: AuthorizationDecision) -> None:
        super().__init__(f"Authorization Denied: {decision.explanation} ({decision.reason_code.value})")
        self.decision = decision


class AuthorizationRequiredError(Exception):
    """Raised when an operation requires explicit human approval before execution."""

    def __init__(self, decision: AuthorizationDecision, approval_id: Optional[str] = None) -> None:
        super().__init__(f"Authorization Required: {decision.explanation} ({decision.reason_code.value})")
        self.decision = decision
        self.approval_id = approval_id


class AuthorizationEngine:
    """Central deterministic authorization authority for AUTONOM."""

    _instance: Optional["AuthorizationEngine"] = None

    def __init__(self) -> None:
        self.emergency_controller = get_emergency_stop_controller()
        self._default_policies = get_default_policies()
        self._lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "AuthorizationEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def evaluate(self, request: AuthorizationRequest) -> AuthorizationDecision:
        """Evaluates an authorization request deterministically and logs decision audit."""
        risk = classify_action_risk(request.capability_id, request.action)

        # 1. Emergency Stop Check (Highest Priority Invariant)
        if self.emergency_controller.is_emergency_stop_active:
            decision = AuthorizationDecision(
                outcome=ActionEffect.DENY,
                reason_code=ReasonCode.EMERGENCY_STOP_ACTIVE,
                explanation="Operation blocked: Global Emergency Stop is currently ACTIVE",
                risk_level=risk,
                correlation_id=request.correlation_id or request.actor.correlation_id,
            )
            await self._record_decision(request, decision)
            return decision

        # 2. Automation Pause Check (Applies to non-user autonomous actions)
        if self.emergency_controller.is_automation_paused and request.actor.actor_type != "user":
            decision = AuthorizationDecision(
                outcome=ActionEffect.DENY,
                reason_code=ReasonCode.AUTOMATION_PAUSED,
                explanation="Operation blocked: Background autonomous automation is paused",
                risk_level=risk,
                correlation_id=request.correlation_id or request.actor.correlation_id,
            )
            await self._record_decision(request, decision)
            return decision

        # 3. Security Invariant: Credential term protection for specialist agents
        if request.actor.agent_id and request.actor.agent_id != "supervisor":
            action_lower = f"{request.capability_id}_{request.action}".lower()
            if any(k in action_lower for k in ("credential", "vault", "password", "secret")):
                decision = AuthorizationDecision(
                    outcome=ActionEffect.DENY,
                    reason_code=ReasonCode.CREDENTIAL_ACCESS_RESTRICTED,
                    explanation="Security Invariant: Specialist agents cannot access raw credentials",
                    risk_level=RiskLevel.CRITICAL,
                    correlation_id=request.correlation_id or request.actor.correlation_id,
                )
                await self._record_decision(request, decision)
                return decision

        # 4. Check if exact request already has an approved ApprovalRequest
        digest = request.compute_digest()
        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            existing_approval = await repo.find_approved_approval_by_digest(
                parameters_digest=digest,
                workflow_id=request.actor.workflow_id,
                step_id=request.actor.step_id,
            )
            if existing_approval and existing_approval.status == ApprovalStatus.APPROVED.value:
                now = datetime.now(UTC)
                exp = existing_approval.expires_at
                if exp:
                    if exp.tzinfo is None:
                        exp = exp.replace(tzinfo=UTC)
                    if exp < now:
                        existing_approval = None
                if existing_approval:
                    decision = AuthorizationDecision(
                        outcome=ActionEffect.ALLOW,
                        reason_code=ReasonCode.APPROVAL_GRANTED,
                        explanation=f"Action explicitly approved by user via request '{existing_approval.id}'",
                        risk_level=risk,
                        correlation_id=request.correlation_id or request.actor.correlation_id,
                    )
                    await self._record_decision(request, decision)
                    return decision

        # 5. Check Active Authorization Grants (Preauthorized Autonomy)
        active_grants = await self._load_active_grants(request.actor.agent_id, request.actor.workflow_id)
        for grant in active_grants:
            if evaluate_grant_match(grant, request):
                decision = AuthorizationDecision(
                    outcome=ActionEffect.ALLOW,
                    grant_id=grant.id,
                    reason_code=ReasonCode.PREAUTHORIZED_GRANT,
                    explanation=f"Preauthorized under active grant '{grant.name}' ({grant.id})",
                    risk_level=risk,
                    correlation_id=request.correlation_id or request.actor.correlation_id,
                )
                await self._record_decision(request, decision)
                return decision

        # 6. Evaluate Policies (System Baselines + Custom DB Policies)
        policies = await self._load_all_policies()

        # Step 6a: Check Explicit Denies First
        for pol in policies:
            effect = evaluate_policy_rule(pol, request, risk)
            if effect == ActionEffect.DENY:
                decision = AuthorizationDecision(
                    outcome=ActionEffect.DENY,
                    policy_id=pol.id,
                    reason_code=ReasonCode.EXPLICIT_DENY_POLICY,
                    explanation=f"Operation explicitly denied by policy '{pol.name}' ({pol.id})",
                    risk_level=risk,
                    correlation_id=request.correlation_id or request.actor.correlation_id,
                )
                await self._record_decision(request, decision)
                return decision

        # Step 6b: Check Require Approval Conditions
        for pol in policies:
            effect = evaluate_policy_rule(pol, request, risk)
            if effect == ActionEffect.REQUIRE_APPROVAL:
                decision = AuthorizationDecision(
                    outcome=ActionEffect.REQUIRE_APPROVAL,
                    policy_id=pol.id,
                    reason_code=ReasonCode.APPROVAL_REQUIRED_BY_POLICY,
                    explanation=f"Action requires explicit user approval per policy '{pol.name}' ({pol.id})",
                    risk_level=risk,
                    correlation_id=request.correlation_id or request.actor.correlation_id,
                )
                await self._record_decision(request, decision)
                return decision

        # Step 6c: Check Explicit Allows
        for pol in policies:
            effect = evaluate_policy_rule(pol, request, risk)
            if effect == ActionEffect.ALLOW:
                decision = AuthorizationDecision(
                    outcome=ActionEffect.ALLOW,
                    policy_id=pol.id,
                    reason_code=ReasonCode.EXPLICIT_ALLOW_POLICY,
                    explanation=f"Operation authorized by policy '{pol.name}' ({pol.id})",
                    risk_level=risk,
                    correlation_id=request.correlation_id or request.actor.correlation_id,
                )
                await self._record_decision(request, decision)
                return decision

        # 7. Low-Risk Safe Baseline (Analytical / Read-Only fallback)
        if risk == RiskLevel.LOW:
            decision = AuthorizationDecision(
                outcome=ActionEffect.ALLOW,
                reason_code=ReasonCode.READ_ONLY_BASELINE,
                explanation="Operation permitted under low-risk read-only system baseline",
                risk_level=risk,
                correlation_id=request.correlation_id or request.actor.correlation_id,
            )
            await self._record_decision(request, decision)
            return decision

        # 8. High-Risk Action Guard: Actions classified as High or Critical require approval if no grant allows them
        if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            decision = AuthorizationDecision(
                outcome=ActionEffect.REQUIRE_APPROVAL,
                reason_code=ReasonCode.HIGH_RISK_ACTION,
                explanation=f"{risk.value.capitalize()} risk action requires user approval",
                risk_level=risk,
                correlation_id=request.correlation_id or request.actor.correlation_id,
            )
            await self._record_decision(request, decision)
            return decision

        # 9. Default Deny
        decision = AuthorizationDecision(
            outcome=ActionEffect.DENY,
            reason_code=ReasonCode.DEFAULT_DENY,
            explanation=f"Action '{request.action}' (capability '{request.capability_id}') denied by default",
            risk_level=risk,
            correlation_id=request.correlation_id or request.actor.correlation_id,
        )
        await self._record_decision(request, decision)
        return decision

    async def _load_active_grants(
        self,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> list[GrantDefinition]:
        """Loads non-revoked, unexpired grants from SQLite."""
        grants: list[GrantDefinition] = []
        try:
            async with get_db_session() as session:
                repo = AuthorizationRepository(session)
                records = await repo.list_grants(active_only=True, subject_id=agent_id, workflow_id=workflow_id)
                for r in records:
                    grants.append(
                        GrantDefinition(
                            id=r.id,
                            name=r.name,
                            grant_type=r.grant_type,
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
                    )
        except Exception as e:
            logger.error("Error loading active grants: %s", e)
        return grants

    async def _load_all_policies(self) -> list[PolicyDefinition]:
        """Loads default policies combined with user-defined policies from database."""
        policies = list(self._default_policies)
        try:
            async with get_db_session() as session:
                repo = AuthorizationRepository(session)
                db_records = await repo.list_policies(enabled_only=True)
                for r in db_records:
                    # Don't duplicate defaults if already registered
                    if not any(p.id == r.id for p in policies):
                        policies.append(
                            PolicyDefinition(
                                id=r.id,
                                name=r.name,
                                description=r.description,
                                version=r.version,
                                is_enabled=r.is_enabled,
                                is_system=r.is_system,
                                subject_scope=r.subject_scope,
                                category_scope=r.category_scope,
                                action_scope=r.action_scope_json or [],
                                resource_scope=r.resource_scope_json or {},
                                effect=ActionEffect(r.effect),
                                conditions=r.conditions_json or {},
                            )
                        )
        except Exception as e:
            logger.error("Error loading policies from DB, using baselines: %s", e)
        return policies

    async def _record_decision(
        self,
        request: AuthorizationRequest,
        decision: AuthorizationDecision,
    ) -> None:
        """Persists audit record of the decision."""
        try:
            async with get_db_session() as session:
                repo = AuthorizationRepository(session)
                record = AuthorizationDecisionRecord(
                    id=decision.decision_id,
                    correlation_id=decision.correlation_id,
                    actor_id=request.actor.actor_id,
                    agent_id=request.actor.agent_id,
                    workflow_id=request.actor.workflow_id,
                    step_id=request.actor.step_id,
                    capability_id=request.capability_id,
                    action=request.action,
                    resource_type=request.resource_type,
                    resource_id=request.resource_id,
                    outcome=decision.outcome.value,
                    policy_id=decision.policy_id,
                    grant_id=decision.grant_id,
                    reason_code=decision.reason_code.value,
                    explanation=decision.explanation,
                    timestamp=decision.timestamp,
                )
                await repo.record_decision(record)
        except Exception as e:
            logger.error("Failed to persist authorization decision audit: %s", e)


_auth_engine: Optional[AuthorizationEngine] = None


def get_authorization_engine() -> AuthorizationEngine:
    """Returns singleton AuthorizationEngine instance."""
    global _auth_engine
    if _auth_engine is None:
        _auth_engine = AuthorizationEngine()
    return _auth_engine
