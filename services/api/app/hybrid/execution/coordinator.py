"""Hybrid Action Coordinator executing unified actions with context-aware fallback."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.hybrid.adapters.registry import InteractionAdapterRegistry, get_adapter_registry
from app.hybrid.contracts import (
    HybridActionType,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionResult,
    RoutingDecisionRecordSchema,
)
from app.hybrid.errors import (
    FallbackBlockedError,
    FallbackLimitExceededError,
    NoEligibleMethodError,
    NonIdempotentActionBlockedError,
    StaleTargetError,
)
from app.hybrid.execution.input_ownership import (
    HybridInputOwnershipCoordinator,
    get_input_coordinator,
)
from app.hybrid.execution.verification import HybridVerificationCoordinator
from app.hybrid.routing.fallback import FallbackController
from app.hybrid.routing.router import HybridMethodRouter
from app.hybrid.targets.identity import TargetIdentityValidator

logger = logging.getLogger("autonom.hybrid.execution.coordinator")


class HybridActionCoordinator:
    """Coordinates the Observe -> Route -> Act -> Verify execution pipeline with safe fallback."""

    def __init__(
        self,
        registry: Optional[InteractionAdapterRegistry] = None,
        router: Optional[HybridMethodRouter] = None,
        fallback_controller: Optional[FallbackController] = None,
        input_coordinator: Optional[HybridInputOwnershipCoordinator] = None,
    ) -> None:
        self.registry = registry or get_adapter_registry()
        self.router = router or HybridMethodRouter(registry=self.registry)
        self.fallback_controller = fallback_controller or FallbackController()
        self.input_coordinator = input_coordinator or get_input_coordinator()

    async def execute_action(
        self,
        action: InteractionAction,
    ) -> tuple[InteractionResult, Optional[RoutingDecisionRecordSchema], list[dict[str, Any]]]:
        """Execute unified action with automatic routing, verification, and bounded fallback."""
        start_time = time.perf_counter()
        attempts: list[dict[str, Any]] = []

        # 1. Target Identity and Freshness Validation
        TargetIdentityValidator.validate_target(action.target)

        # 2. Method Routing
        selected_method = action.method
        routing_decision: Optional[RoutingDecisionRecordSchema] = None

        if selected_method is None:
            selected_method, routing_decision = await self.router.route(
                target=action.target,
                action_type=action.action_type,
                preferred_method=None,
                task_id=action.task_id,
            )

        # 3. Input Lease Acquisition (for physical mouse/keyboard actions)
        needs_input_lease = selected_method in (InteractionMethod.VISUAL_GROUNDING, InteractionMethod.WINDOWS_WIN32)
        lease_acquired = False
        if needs_input_lease:
            lease_acquired = await self.input_coordinator.acquire_lease(owner_id=action.action_id)

        current_method = selected_method
        fallback_count = 0
        final_result: Optional[InteractionResult] = None

        try:
            while True:
                adapter = self.registry.get(current_method)
                if not adapter:
                    raise KeyError(f"Adapter for method {current_method.value} not found")

                attempt_start = time.perf_counter()
                action_copy = action.model_copy()
                action_copy.method = current_method

                result = await adapter.execute(action_copy)

                # Verify if action reported success
                if result.success:
                    ver_status = await HybridVerificationCoordinator.verify_action(
                        adapter=adapter,
                        action=action_copy,
                        result=result,
                    )
                    result.verification_status = ver_status
                    if ver_status == HybridVerificationStatus.FAILED:
                        result.success = False
                        result.error_message = (
                            result.error_message or "Post-action verification failed to detect expected mutation"
                        )

                attempt_duration_ms = (time.perf_counter() - attempt_start) * 1000
                self.registry.record_attempt(
                    method=current_method,
                    success=result.success,
                    latency_ms=attempt_duration_ms,
                    error=result.error_message,
                )

                attempts.append({
                    "step": fallback_count + 1,
                    "method": current_method.value,
                    "success": result.success,
                    "verification": result.verification_status.value,
                    "duration_ms": round(attempt_duration_ms, 2),
                    "error": result.error_message,
                })

                if result.success:
                    final_result = result
                    final_result.fallback_occurred = (fallback_count > 0)
                    final_result.fallback_attempts = fallback_count
                    break

                # Execution or verification failed. Evaluate fallback candidates.
                if not action.allow_fallback or fallback_count >= self.fallback_controller.max_fallback_steps:
                    final_result = result
                    final_result.fallback_occurred = (fallback_count > 0)
                    final_result.fallback_attempts = fallback_count
                    break

                # Find alternative candidate methods from routing decision or probes
                remaining_candidates: list[InteractionMethod] = []
                if routing_decision and routing_decision.candidate_methods:
                    remaining_candidates = [
                        m for m in routing_decision.candidate_methods
                        if m != current_method and m not in [att["method"] for att in attempts]
                    ]

                if not remaining_candidates:
                    # No other candidates remaining
                    final_result = result
                    final_result.fallback_occurred = (fallback_count > 0)
                    final_result.fallback_attempts = fallback_count
                    break

                candidate = remaining_candidates[0]

                # Check fallback eligibility (including non-idempotent action protections)
                try:
                    self.fallback_controller.validate_fallback_eligibility(
                        action=action,
                        initial_result=result,
                        candidate_method=candidate,
                        current_step=fallback_count,
                    )
                except (FallbackBlockedError, NonIdempotentActionBlockedError, FallbackLimitExceededError) as exc:
                    logger.warning("Fallback blocked: %s", exc)
                    final_result = result
                    final_result.fallback_occurred = (fallback_count > 0)
                    final_result.fallback_attempts = fallback_count
                    break

                # Transition to next method
                logger.info(
                    "Executing fallback from %s to %s for action %s",
                    current_method.value,
                    candidate.value,
                    action.action_id,
                )
                current_method = candidate
                fallback_count += 1

        finally:
            if lease_acquired:
                self.input_coordinator.release_lease(owner_id=action.action_id)

        if final_result is None:
            final_result = InteractionResult(
                action_id=action.action_id,
                method=selected_method,
                success=False,
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
                verification_status=HybridVerificationStatus.FAILED,
                error_message="Action execution completed without a valid result",
            )

        return final_result, routing_decision, attempts
