"""Base class and Protocol definitions for Specialist Agents in AUTONOM (Stage 13)."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
import logging
from typing import Any
import uuid

from app.orchestration.agents.contracts import (
    AgentManifest,
    AgentRequest,
    AgentResult,
    AvailabilityState,
)
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.contracts import FailureCategory, VerificationStatus

logger = logging.getLogger("autonom.orchestration.agents.base")


class SpecialistAgent(ABC):
    """Abstract Base Class for all autonomous specialist agents."""

    def __init__(self, manifest: AgentManifest) -> None:
        self._manifest = manifest
        self._active_executions: set[str] = set()

    @property
    def manifest(self) -> AgentManifest:
        """Return the immutable or configured manifest of this agent."""
        return self._manifest

    @property
    def agent_id(self) -> str:
        return self._manifest.agent_id

    @property
    def name(self) -> str:
        return self._manifest.name

    @property
    def category(self) -> str:
        return self._manifest.category.value

    @property
    def is_available(self) -> bool:
        return (
            self._manifest.enabled
            and self._manifest.availability_state in (AvailabilityState.OPERATIONAL, AvailabilityState.LIMITED)
        )

    def validate_input(self, capability_id: str, input_data: dict[str, Any]) -> tuple[bool, str | None]:
        """Validate input payload against agent capability constraints and context policy."""
        if capability_id not in self._manifest.capabilities:
            return False, f"Capability '{capability_id}' not supported by agent '{self.agent_id}'"

        # Check context isolation / disallowed keys
        if not self._manifest.context_policy.allow_credentials:
            for k in ("credential", "api_key", "password", "secret", "token"):
                if k in input_data or any(k in str(v).lower() for v in input_data.keys()):
                    return False, f"Context policy violation: credentials not permitted in agent '{self.agent_id}' input"

        return True, None

    async def execute(self, request: AgentRequest) -> AgentResult:
        """Execute a specialist task request.
        
        Default implementation delegates to the capability registry or specialist handler.
        """
        if not self.is_available:
            return AgentResult(
                agent_id=self.agent_id,
                capability_id=request.capability_id,
                status="failed",
                error_category=FailureCategory.MISSING_CAPABILITY,
                error_message=f"Agent '{self.agent_id}' is not currently available ({self._manifest.availability_state.value}).",
                verification_status=VerificationStatus.FAIL,
            )

        valid, err = self.validate_input(request.capability_id, request.input_data)
        if not valid:
            return AgentResult(
                agent_id=self.agent_id,
                capability_id=request.capability_id,
                status="failed",
                error_category=FailureCategory.INVALID_OUTPUT,
                error_message=err or "Input validation failed",
                verification_status=VerificationStatus.FAIL,
            )

        start_time = datetime.now(UTC)
        execution_id = f"exec_{uuid.uuid4().hex[:10]}"
        self._active_executions.add(execution_id)

        try:
            # Execute through specialist execution hook or fallback to capability registry
            output = await self.execute_capability(request.capability_id, request.input_data, request.context)
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            return AgentResult(
                execution_id=execution_id,
                agent_id=self.agent_id,
                capability_id=request.capability_id,
                status="completed",
                output_data=output,
                verification_status=VerificationStatus.PASS,
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            logger.error("Agent '%s' failed executing '%s': %s", self.agent_id, request.capability_id, exc)
            return AgentResult(
                execution_id=execution_id,
                agent_id=self.agent_id,
                capability_id=request.capability_id,
                status="failed",
                error_category=FailureCategory.INVALID_OUTPUT,
                error_message=str(exc),
                verification_status=VerificationStatus.FAIL,
                duration_ms=duration_ms,
            )
        finally:
            self._active_executions.discard(execution_id)

    async def execute_capability(
        self,
        capability_id: str,
        input_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Override in subclasses for direct execution, or default to CapabilityRegistry."""
        cap_reg = get_capability_registry()
        return await cap_reg.execute(capability_id, input_data, context)

    async def cancel(self, execution_id: str) -> None:
        """Cancel an in-flight execution."""
        if execution_id in self._active_executions:
            self._active_executions.discard(execution_id)
            logger.info("Agent '%s' cancelled execution '%s'", self.agent_id, execution_id)
