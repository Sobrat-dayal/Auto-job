"""Unit tests for Hybrid Action Coordinator, State Machine, and Input Ownership."""

import pytest
from app.hybrid.adapters.base import BaseInteractionAdapter
from app.hybrid.adapters.registry import InteractionAdapterRegistry
from app.hybrid.contracts import (
    CapabilityProbe,
    HybridActionType,
    HybridTaskStatus,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionObservation,
    InteractionResult,
    InteractionTarget,
    ObservationRequest,
    SurfaceType,
    TargetType,
)
from app.hybrid.execution.coordinator import HybridActionCoordinator
from app.hybrid.execution.input_ownership import HybridInputOwnershipCoordinator
from app.hybrid.execution.state_machine import HybridStateMachine
from app.hybrid.routing.fallback import FallbackController
from app.hybrid.routing.router import HybridMethodRouter


class FlakyDOMAdapter(BaseInteractionAdapter):
    """Adapter that fails DOM on first try to trigger fallback to Visual."""

    def __init__(self) -> None:
        super().__init__(method=InteractionMethod.BROWSER_DOM)
        self.call_count = 0

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        return CapabilityProbe(
            method=self.method,
            is_available=True,
            is_applicable=True,
            supported_actions=["click"],
            resource_cost_score=1,
        )

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        return InteractionObservation(
            target_id=request.target.target_id,
            method=self.method,
            surface_type=SurfaceType.BROWSER_DOM,
        )

    async def execute(self, request: InteractionAction) -> InteractionResult:
        self.call_count += 1
        return InteractionResult(
            action_id=request.action_id,
            method=self.method,
            success=False,
            verification_status=HybridVerificationStatus.FAILED,
            error_message="Simulated DOM node detached from DOM tree",
        )

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        return HybridVerificationStatus.FAILED


class SuccessfulVisualAdapter(BaseInteractionAdapter):
    """Visual adapter that succeeds when called as fallback."""

    def __init__(self) -> None:
        super().__init__(method=InteractionMethod.VISUAL_GROUNDING)
        self.call_count = 0

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        return CapabilityProbe(
            method=self.method,
            is_available=True,
            is_applicable=True,
            supported_actions=["click"],
            resource_cost_score=4,
        )

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        return InteractionObservation(
            target_id=request.target.target_id,
            method=self.method,
            surface_type=SurfaceType.CUSTOM_RENDERED,
        )

    async def execute(self, request: InteractionAction) -> InteractionResult:
        self.call_count += 1
        return InteractionResult(
            action_id=request.action_id,
            method=self.method,
            success=True,
            verification_status=HybridVerificationStatus.SUCCESS,
            mutation_detected=True,
        )

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        return HybridVerificationStatus.SUCCESS


@pytest.mark.asyncio
async def test_hybrid_action_coordinator_automatic_fallback() -> None:
    """Verifies that when primary routed method fails, coordinator automatically falls back to secondary candidate."""
    registry = InteractionAdapterRegistry()
    flaky_dom = FlakyDOMAdapter()
    succ_vis = SuccessfulVisualAdapter()
    registry.register(flaky_dom)
    registry.register(succ_vis)

    router = HybridMethodRouter(registry=registry)
    fallback_ctrl = FallbackController(max_fallback_steps=3)
    coordinator = HybridActionCoordinator(
        registry=registry,
        router=router,
        fallback_controller=fallback_ctrl,
    )

    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="button#apply",
    )
    action = InteractionAction(
        target=target,
        action_type=HybridActionType.CLICK,
        allow_fallback=True,
    )

    result, routing_dec, attempts = await coordinator.execute_action(action)

    assert result.success is True
    assert result.method == InteractionMethod.VISUAL_GROUNDING
    assert result.fallback_occurred is True
    assert result.fallback_attempts == 1
    assert len(attempts) == 2
    assert attempts[0]["method"] == "BROWSER_DOM"
    assert attempts[0]["success"] is False
    assert attempts[1]["method"] == "VISUAL_GROUNDING"
    assert attempts[1]["success"] is True


@pytest.mark.asyncio
async def test_input_ownership_lease_acquisition_and_release() -> None:
    """Verifies input lease acquisition, mutual exclusion, and clean release."""
    coordinator = HybridInputOwnershipCoordinator()

    # Acquire lease for task A
    acquired_a = await coordinator.acquire_lease(owner_id="task_A")
    assert acquired_a is True
    assert coordinator.current_owner == "task_A"

    # Task B cannot acquire while task A holds it
    acquired_b = await coordinator.acquire_lease(owner_id="task_B", timeout_seconds=0.1)
    assert acquired_b is False
    assert coordinator.current_owner == "task_A"

    # Task A releases lease
    coordinator.release_lease(owner_id="task_A")
    assert coordinator.current_owner is None

    # Now task B can acquire
    acquired_b2 = await coordinator.acquire_lease(owner_id="task_B")
    assert acquired_b2 is True
    assert coordinator.current_owner == "task_B"
    coordinator.release_lease(owner_id="task_B")


def test_hybrid_state_machine_valid_and_invalid_transitions() -> None:
    """Verifies deterministic task lifecycle state machine."""
    sm = HybridStateMachine(initial_status=HybridTaskStatus.PENDING)
    assert sm.current_status == HybridTaskStatus.PENDING

    sm.transition_to(HybridTaskStatus.ROUTING)
    assert sm.current_status == HybridTaskStatus.ROUTING

    sm.transition_to(HybridTaskStatus.EXECUTING)
    assert sm.current_status == HybridTaskStatus.EXECUTING

    sm.transition_to(HybridTaskStatus.VERIFYING)
    assert sm.current_status == HybridTaskStatus.VERIFYING

    sm.transition_to(HybridTaskStatus.COMPLETED)
    assert sm.current_status == HybridTaskStatus.COMPLETED

    # Terminal state cannot transition to EXECUTING
    with pytest.raises(ValueError):
        sm.transition_to(HybridTaskStatus.EXECUTING)
