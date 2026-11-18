"""Tests for visual action execution, verification, and recovery (Stage 18)."""

import pytest
from PIL import Image
from app.visual.contracts import (
    CapturedFrame,
    FrameMetadata,
    Point2D,
    VerificationStatus,
    VisualActionRequest,
    VisualActionResult,
    VisualActionType,
    VisualTaskStatus,
)
from app.visual.execution.recovery import VisualRecoveryManager
from app.visual.execution.state_machine import VisualStateMachine
from app.visual.execution.verification import VisualActionVerifier
from app.visual.input.ownership import InputOwnershipManager
from app.visual.security.guard import visual_security_guard


def test_input_ownership_lease():
    """Test acquiring, holding, and releasing exclusive input leases."""
    mgr = InputOwnershipManager()
    token = mgr.acquire_lease("agent_1", duration_seconds=5.0)
    assert token is not None
    assert mgr.is_lease_active(token) is True

    # Conflicting lease attempt from another agent without force should fail
    conflicting = mgr.acquire_lease("agent_2", duration_seconds=5.0)
    assert conflicting is None

    # Release lease
    released = mgr.release_lease(token)
    assert released is True
    assert mgr.is_lease_active(token) is False


def test_visual_state_machine_lifecycle():
    """Test state machine valid transitions and illegal transition rejection."""
    sm = VisualStateMachine("task_123")
    assert sm.current_status == VisualTaskStatus.PENDING

    # PENDING -> OBSERVING
    assert sm.transition_to(VisualTaskStatus.OBSERVING, "Observing frame") is True
    # OBSERVING -> GROUNDING
    assert sm.transition_to(VisualTaskStatus.GROUNDING, "Grounding element") is True
    # GROUNDING -> ACTING
    assert sm.transition_to(VisualTaskStatus.ACTING, "Executing input") is True
    # ACTING -> VERIFYING
    assert sm.transition_to(VisualTaskStatus.VERIFYING, "Verifying change") is True
    # VERIFYING -> COMPLETED
    assert sm.transition_to(VisualTaskStatus.COMPLETED, "Done") is True

    assert sm.is_terminal is True
    # Attempting to transition out of terminal state must fail
    assert sm.transition_to(VisualTaskStatus.ACTING, "Illegal") is False


@pytest.mark.asyncio
async def test_recovery_manager_bounded_retries():
    """Test that VisualRecoveryManager respects max retry limits and does not loop infinitely."""
    from unittest.mock import AsyncMock, MagicMock

    session_mgr = MagicMock()
    grounding_svc = MagicMock()
    recovery = VisualRecoveryManager(session_mgr, grounding_svc, max_attempts=2, backoff_seconds=0.01)

    failed_result = VisualActionResult(
        success=False,
        action_type=VisualActionType.CLICK,
        verification_status=VerificationStatus.FAILED,
        execution_time_ms=10.0,
        visual_difference=0.0,
    )

    action_fn = AsyncMock(return_value=failed_result)

    final = await recovery.attempt_recovery(
        session_id="test_sess",
        query="nonexistent_button",
        failed_result=failed_result,
        action_fn=action_fn,
        attempt=1,
    )

    assert final.verification_status == VerificationStatus.FAILED
    assert len(recovery.history) <= 3
