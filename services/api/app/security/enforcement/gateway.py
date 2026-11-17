"""Secure Tool Execution Gateway enforcing authorization, input validation, and execution bounds."""

from datetime import UTC, datetime
import logging
from typing import Any, Callable, Optional

from app.db.engine import get_db_session
from app.db.models import AuditEventModel
from app.orchestration.capabilities.registry import get_capability_registry
from app.repositories.authorization_repository import AuthorizationRepository
from app.security.authorization.approvals import get_approval_manager
from app.security.authorization.contracts import (
    ActionEffect,
    ActorContext,
    ApprovalMode,
    AuthorizationRequest,
    ReasonCode,
    RiskLevel,
)
from app.security.authorization.emergency import get_emergency_stop_controller
from app.security.authorization.engine import (
    AuthorizationDeniedError,
    AuthorizationRequiredError,
    get_authorization_engine,
)

logger = logging.getLogger("autonom.security.enforcement.gateway")


class ToolExecutionGateway:
    """Central enforcement point for tool and capability execution."""

    def __init__(self) -> None:
        self.auth_engine = get_authorization_engine()
        self.approval_manager = get_approval_manager()
        self.emergency_controller = get_emergency_stop_controller()
        self.capabilities = get_capability_registry()

    async def execute_capability(
        self,
        capability_id: str,
        parameters: dict[str, Any],
        actor: ActorContext,
        action: Optional[str] = None,
        resource_type: str = "general",
        resource_id: Optional[str] = None,
        resource_scope: Optional[dict[str, Any]] = None,
        custom_handler: Optional[Callable[[dict[str, Any]], Any]] = None,
    ) -> Any:
        """Executes a capability or tool through strict pre-execution authorization and audit logging."""
        action_name = action or capability_id
        scope = resource_scope or {}

        # 1. Build strongly typed authorization request
        auth_request = AuthorizationRequest(
            actor=actor,
            capability_id=capability_id,
            action=action_name,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_scope=scope,
            parameters=parameters,
            context={"step_id": actor.step_id, "workflow_id": actor.workflow_id},
            correlation_id=actor.correlation_id,
        )

        # 2. Evaluate through Authorization Engine
        decision = await self.auth_engine.evaluate(auth_request)

        # 3. Handle Denials
        if decision.outcome == ActionEffect.DENY:
            logger.warning(
                "Execution DENIED for capability '%s' by agent '%s': %s (%s)",
                capability_id,
                actor.agent_id,
                decision.explanation,
                decision.reason_code.value,
            )
            await self._record_audit_event(
                actor=actor,
                action_type=action_name,
                resource_type=resource_type,
                resource_id=resource_id,
                outcome="denied",
                metadata={"reason": decision.explanation, "reason_code": decision.reason_code.value},
            )
            raise AuthorizationDeniedError(decision)

        # 4. Handle Approval Required
        if decision.outcome == ActionEffect.REQUIRE_APPROVAL:
            logger.info(
                "Execution REQUIRES APPROVAL for capability '%s' by agent '%s': %s",
                capability_id,
                actor.agent_id,
                decision.explanation,
            )
            approval = await self.approval_manager.create_or_get_request(
                auth_request=auth_request,
                risk_level=decision.risk_level,
                reason=decision.explanation,
                approval_mode=ApprovalMode.ONE_TIME,
            )
            await self._record_audit_event(
                actor=actor,
                action_type=action_name,
                resource_type=resource_type,
                resource_id=resource_id,
                outcome="approval_required",
                metadata={"approval_id": approval.id, "risk": decision.risk_level.value},
            )
            raise AuthorizationRequiredError(decision, approval_id=approval.id)

        # 5. Just-In-Time TOCTOU Revalidation (Check Emergency Stop immediately before execution)
        if self.emergency_controller.is_emergency_stop_active:
            raise AuthorizationDeniedError(
                decision.model_copy(
                    update={
                        "outcome": ActionEffect.DENY,
                        "reason_code": ReasonCode.EMERGENCY_STOP_ACTIVE,
                        "explanation": "Aborted: Emergency Stop triggered prior to invocation",
                    }
                )
            )

        # 6. Consume approval if request was authorized via an approval
        if decision.reason_code == ReasonCode.APPROVAL_GRANTED:
            digest = auth_request.compute_digest()
            async with get_db_session() as session:
                repo = AuthorizationRepository(session)
                existing = await repo.find_pending_approval_by_digest(
                    parameters_digest=digest,
                    workflow_id=actor.workflow_id,
                    step_id=actor.step_id,
                )
                if existing and existing.status == "approved":
                    await self.approval_manager.consume_request(existing.id)

        # 7. Increment grant use if authorized via grant
        if decision.grant_id:
            try:
                async with get_db_session() as session:
                    repo = AuthorizationRepository(session)
                    await repo.increment_grant_use(decision.grant_id)
            except Exception as e:
                logger.error("Failed to increment grant usage: %s", e)

        # 8. Execute Handler
        try:
            if custom_handler:
                result = await custom_handler(parameters)
            else:
                handler = self.capabilities.get(capability_id)
                if not handler:
                    raise KeyError(f"Capability '{capability_id}' not found in registry")
                result = await handler.execute(parameters)

            await self._record_audit_event(
                actor=actor,
                action_type=action_name,
                resource_type=resource_type,
                resource_id=resource_id,
                outcome="success",
                metadata={"capability_id": capability_id, "grant_id": decision.grant_id},
            )
            return result
        except Exception as e:
            await self._record_audit_event(
                actor=actor,
                action_type=action_name,
                resource_type=resource_type,
                resource_id=resource_id,
                outcome="failed",
                metadata={"error": str(e), "capability_id": capability_id},
            )
            raise

    async def _record_audit_event(
        self,
        actor: ActorContext,
        action_type: str,
        resource_type: str,
        resource_id: Optional[str],
        outcome: str,
        metadata: dict[str, Any],
    ) -> None:
        """Records an execution event to the persistent audit ledger."""
        try:
            async with get_db_session() as session:
                audit_record = AuditEventModel(
                    actor_id=actor.agent_id or actor.actor_id,
                    action_type=action_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    outcome=outcome,
                    timestamp=datetime.now(UTC),
                    correlation_id=actor.correlation_id,
                    safe_metadata_json=metadata,
                )
                session.add(audit_record)
                await session.commit()
        except Exception as e:
            logger.error("Failed to write to audit ledger: %s", e)


_tool_gateway: Optional[ToolExecutionGateway] = None


def get_tool_execution_gateway() -> ToolExecutionGateway:
    """Returns singleton ToolExecutionGateway."""
    global _tool_gateway
    if _tool_gateway is None:
        _tool_gateway = ToolExecutionGateway()
    return _tool_gateway
