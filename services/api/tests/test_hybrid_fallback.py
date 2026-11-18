"""Unit tests for Context-Aware Fallback Controller and non-idempotent action safety."""

import pytest
from app.hybrid.contracts import (
    ActionRiskLevel,
    HybridActionType,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionResult,
    InteractionTarget,
    SurfaceType,
    TargetType,
)
from app.hybrid.errors import (
    FallbackBlockedError,
    FallbackLimitExceededError,
    NonIdempotentActionBlockedError,
)
from app.hybrid.routing.fallback import FallbackController


@pytest.fixture
def fallback_controller() -> FallbackController:
    return FallbackController(max_fallback_steps=3)


def test_fallback_eligibility_permitted(fallback_controller: FallbackController) -> None:
    """Verifies that normal repeatable action failure allows fallback to eligible candidate."""
    action = InteractionAction(
        target=InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.BROWSER_DOM),
        action_type=HybridActionType.CLICK,
        risk_level=ActionRiskLevel.REPEATABLE,
    )
    initial_res = InteractionResult(
        action_id=action.action_id,
        method=InteractionMethod.BROWSER_DOM,
        success=False,
        verification_status=HybridVerificationStatus.FAILED,
        error_message="DOM element not found",
    )
    # Fallback to UIA or Visual should be permitted
    fallback_controller.validate_fallback_eligibility(
        action=action,
        initial_result=initial_res,
        candidate_method=InteractionMethod.WINDOWS_UIA,
        current_step=0,
    )


def test_fallback_limit_exceeded_aborts(fallback_controller: FallbackController) -> None:
    """Verifies that exceeding max_fallback_steps raises FallbackLimitExceededError to prevent infinite loops."""
    action = InteractionAction(
        target=InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.BROWSER_DOM),
        action_type=HybridActionType.CLICK,
    )
    initial_res = InteractionResult(
        action_id=action.action_id,
        method=InteractionMethod.BROWSER_DOM,
        success=False,
    )
    with pytest.raises(FallbackLimitExceededError) as exc_info:
        fallback_controller.validate_fallback_eligibility(
            action=action,
            initial_result=initial_res,
            candidate_method=InteractionMethod.VISUAL_GROUNDING,
            current_step=3,  # Already at max_steps (3)
        )
    assert "Maximum fallback depth of 3 exceeded" in str(exc_info.value)


def test_fallback_explicitly_disallowed(fallback_controller: FallbackController) -> None:
    """Verifies that action with allow_fallback=False raises FallbackBlockedError."""
    action = InteractionAction(
        target=InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.BROWSER_DOM),
        action_type=HybridActionType.CLICK,
        allow_fallback=False,
    )
    initial_res = InteractionResult(
        action_id=action.action_id,
        method=InteractionMethod.BROWSER_DOM,
        success=False,
    )
    with pytest.raises(FallbackBlockedError) as exc_info:
        fallback_controller.validate_fallback_eligibility(
            action=action,
            initial_result=initial_res,
            candidate_method=InteractionMethod.WINDOWS_UIA,
            current_step=0,
        )
    assert "explicitly disallows fallback" in str(exc_info.value)


def test_fallback_same_method_rejected(fallback_controller: FallbackController) -> None:
    """Verifies that falling back to the exact same method that failed is blocked."""
    action = InteractionAction(
        target=InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.BROWSER_DOM),
        action_type=HybridActionType.CLICK,
    )
    initial_res = InteractionResult(
        action_id=action.action_id,
        method=InteractionMethod.BROWSER_DOM,
        success=False,
    )
    with pytest.raises(FallbackBlockedError) as exc_info:
        fallback_controller.validate_fallback_eligibility(
            action=action,
            initial_result=initial_res,
            candidate_method=InteractionMethod.BROWSER_DOM,  # Same as failed method
            current_step=0,
        )
    assert "identical to the failed method" in str(exc_info.value)


def test_non_idempotent_action_unknown_outcome_blocked(fallback_controller: FallbackController) -> None:
    """Verifies that non-idempotent actions (e.g. submit) with UNKNOWN_OUTCOME block blind retry on fallback."""
    action = InteractionAction(
        target=InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.BROWSER_DOM),
        action_type=HybridActionType.SUBMIT,
        risk_level=ActionRiskLevel.NON_IDEMPOTENT,
        is_non_idempotent=True,
    )
    initial_res = InteractionResult(
        action_id=action.action_id,
        method=InteractionMethod.BROWSER_DOM,
        success=False,
        verification_status=HybridVerificationStatus.UNKNOWN_OUTCOME,  # Uncertain state!
        error_message="Network connection closed while waiting for HTTP 200 submit response",
    )
    with pytest.raises(NonIdempotentActionBlockedError) as exc_info:
        fallback_controller.validate_fallback_eligibility(
            action=action,
            initial_result=initial_res,
            candidate_method=InteractionMethod.VISUAL_GROUNDING,
            current_step=0,
        )
    assert "is non-idempotent and initial outcome is unknown" in str(exc_info.value)
