"""Task Router Agent coordinating capability matching, agent dispatch, and explainable routing."""

import logging
from typing import Any

from pydantic import BaseModel, Field

from app.orchestration.agents.registry import AgentRegistry, get_agent_registry
from app.orchestration.capabilities.registry import CapabilityRegistry, get_capability_registry
from app.orchestration.contracts import WorkflowStepDefinition

logger = logging.getLogger("autonom.orchestration.router")


class StepRoutingDecision(BaseModel):
    """Explainable routing decision for assigning a workflow step to an execution agent."""

    step_id: str
    capability_id: str
    assigned_agent_id: str
    assigned_agent_name: str
    is_fallback: bool = False
    explanation: str
    candidates_considered: list[str] = Field(default_factory=list)
    requires_authorization: bool = False
    estimated_duration_seconds: int = 30


class TaskRouterAgent:
    """Agent matching step capability requirements to capable agents and execution handlers."""

    def __init__(
        self,
        agent_registry: AgentRegistry | None = None,
        capability_registry: CapabilityRegistry | None = None,
    ) -> None:
        self.agent_registry = agent_registry or get_agent_registry()
        self.capability_registry = capability_registry or get_capability_registry()
        # Track currently active running assignments per agent for concurrency controls
        self._active_assignments: dict[str, int] = {}

    def route_step(
        self,
        step: WorkflowStepDefinition,
        active_counts: dict[str, int] | None = None,
    ) -> StepRoutingDecision:
        """Evaluate step requirements and select the most qualified, available agent."""
        cap_id = step.capability_id
        cap_handler = self.capability_registry.get(cap_id)
        if not cap_handler:
            logger.warning("No capability handler registered for '%s'", cap_id)

        # 1. Candidate agents from registry
        candidates = self.agent_registry.find_agents_for_capability(cap_id)
        candidate_ids = [c.agent_id for c in candidates]

        active_map = active_counts or self._active_assignments

        # 2. Filter by concurrency limits
        eligible: list[Any] = []
        for agent in candidates:
            current_active = active_map.get(agent.agent_id, 0)
            if current_active < agent.concurrency_limit:
                eligible.append(agent)

        selected_agent = None
        is_fallback = False
        explanation = ""

        if eligible:
            # Pick first eligible candidate
            selected_agent = eligible[0]
            explanation = (
                f"Assigned to '{selected_agent.name}' ({selected_agent.agent_id}) "
                f"which directly provides capability '{cap_id}' (active: {active_map.get(selected_agent.agent_id, 0)}/{selected_agent.concurrency_limit})."
            )
        elif candidates:
            # All primary candidates at concurrency capacity; use capability_worker as fallback if under capacity
            fallback = self.agent_registry.get("capability_worker")
            if fallback and fallback.is_available and active_map.get("capability_worker", 0) < fallback.concurrency_limit:
                selected_agent = fallback
                is_fallback = True
                explanation = (
                    f"Primary agents for '{cap_id}' ({candidate_ids}) at concurrency capacity; "
                    f"routed to general 'Safe Capability Worker'."
                )
            else:
                # Force assignment to primary despite queueing
                selected_agent = candidates[0]
                explanation = f"Queued for '{selected_agent.name}' upon concurrency slot release."
        else:
            # Default fallback to capability_worker
            fallback = self.agent_registry.get("capability_worker")
            if fallback and fallback.is_available:
                selected_agent = fallback
                is_fallback = True
                explanation = f"Routed to general '{fallback.name}' via capability registry execution."
            else:
                raise RuntimeError(f"No available or eligible agent capable of executing '{cap_id}'")

        return StepRoutingDecision(
            step_id=step.step_id,
            capability_id=cap_id,
            assigned_agent_id=selected_agent.agent_id,
            assigned_agent_name=selected_agent.name,
            is_fallback=is_fallback,
            explanation=explanation,
            candidates_considered=candidate_ids,
            requires_authorization=step.requires_authorization,
            estimated_duration_seconds=cap_handler.timeout_seconds if cap_handler else 30,
        )

    def record_start(self, agent_id: str) -> None:
        """Increment active execution counter for agent."""
        self._active_assignments[agent_id] = self._active_assignments.get(agent_id, 0) + 1

    def record_finish(self, agent_id: str) -> None:
        """Decrement active execution counter for agent."""
        curr = self._active_assignments.get(agent_id, 0)
        self._active_assignments[agent_id] = max(0, curr - 1)
