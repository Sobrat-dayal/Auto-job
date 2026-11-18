"""Context-Aware Fallback Controller for the Hybrid Engine."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.contracts import (
    ActionRiskLevel,
    FallbackRecordSchema,
    HybridActionType,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionResult,
    InteractionTarget,
)
from app.hybrid.errors import (
    FallbackBlockedError,
    FallbackLimitExceededError,
    NonIdempotentActionBlockedError,
)
from app.hybrid.routing.policies import RoutingPolicies

logger = logging.getLogger("autonom.hybrid.routing.fallback")


class FallbackController:
    """Manages safe, context-aware method switching and safeguards against blind action replays."""

    def __init__(self, max_fallback_steps: int = 3) -> None:
        self.max_fallback_steps = max_fallback_steps

    def validate_fallback_eligibility(
        self,
        action: InteractionAction,
        initial_result: InteractionResult,
        candidate_method: InteractionMethod,
        current_step: int,
    ) -> None:
        """Validate whether fallback to a candidate method is permitted."""
        # 1. Bounded fallback depth check
        if current_step >= self.max_fallback_steps:
            raise FallbackLimitExceededError(
                f"Maximum fallback depth of {self.max_fallback_steps} exceeded. Aborting to prevent infinite loops.",
                details={"action_id": action.action_id, "current_step": current_step},
            )

        # 2. Check if action explicitly forbids fallback
        if not action.allow_fallback:
            raise FallbackBlockedError(
                f"Action '{action.action_id}' explicitly disallows fallback.",
                details={"action_id": action.action_id},
            )

        # 3. Non-idempotent action protection:
        # If action is non-idempotent or irreversible and the outcome was unknown,
        # blind retry via another method could cause duplicate submissions, purchases, or data corruption!
        is_non_idempotent = action.is_non_idempotent or RoutingPolicies.is_action_non_idempotent(
            action.action_type,
            action.risk_level,
        )

        if is_non_idempotent and initial_result.verification_status == HybridVerificationStatus.UNKNOWN_OUTCOME:
            raise NonIdempotentActionBlockedError(
                f"Action '{action.action_type.value}' is non-idempotent and initial outcome is unknown. "
                "Automatic method fallback is blocked to prevent duplicate external side-effects.",
                details={
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "initial_method": initial_result.method.value,
                    "verification_status": initial_result.verification_status.value,
                },
            )

        # 4. Do not fallback to the exact same method that just failed
        if candidate_method == initial_result.method:
            raise FallbackBlockedError(
                f"Candidate fallback method '{candidate_method.value}' is identical to the failed method.",
                details={"method": candidate_method.value},
            )

        logger.info(
            "Fallback permitted: %s -> %s for action %s (step %d)",
            initial_result.method.value,
            candidate_method.value,
            action.action_id,
            current_step,
        )

    def record_fallback(
        self,
        task_id: str,
        initial_method: InteractionMethod,
        fallback_method: InteractionMethod,
        trigger_reason: str,
        outcome: str = "success",
    ) -> FallbackRecordSchema:
        """Create an audit record for the fallback event."""
        return FallbackRecordSchema(
            task_id=task_id,
            initial_method=initial_method,
            fallback_method=fallback_method,
            trigger_reason=trigger_reason,
            reobservation_successful=True,
            outcome=outcome,
        )
