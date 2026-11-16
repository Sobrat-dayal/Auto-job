"""Unit tests for the task state machine and transition validator."""

import pytest

from app.core.exceptions import InvalidTaskTransitionError
from app.execution.state_machine import validate_transition
from app.schemas.tasks import TaskState


def test_valid_transitions():
    """Confirms all architectural valid state transitions succeed without error."""
    # Creation to queue
    validate_transition(TaskState.CREATED, TaskState.QUEUED)
    validate_transition(TaskState.CREATED, TaskState.CANCELLED)

    # Queue to planning or running
    validate_transition(TaskState.QUEUED, TaskState.PLANNING)
    validate_transition(TaskState.QUEUED, TaskState.RUNNING)
    validate_transition(TaskState.QUEUED, TaskState.CANCELLED)

    # Running to terminal or intermediate states
    validate_transition(TaskState.RUNNING, TaskState.COMPLETED)
    validate_transition(TaskState.RUNNING, TaskState.FAILED)
    validate_transition(TaskState.RUNNING, TaskState.CANCELLED)
    validate_transition(TaskState.RUNNING, TaskState.PAUSED)
    validate_transition(TaskState.RUNNING, TaskState.WAITING_FOR_AUTHORIZATION)
    validate_transition(TaskState.RUNNING, TaskState.RETRYING)

    # Paused back to running
    validate_transition(TaskState.PAUSED, TaskState.RUNNING)
    validate_transition(TaskState.PAUSED, TaskState.CANCELLED)

    # Self-transition is a no-op
    validate_transition(TaskState.RUNNING, TaskState.RUNNING)


def test_invalid_transitions():
    """Confirms illegal transitions raise InvalidTaskTransitionError."""
    # Terminal states cannot transition anywhere
    with pytest.raises(InvalidTaskTransitionError) as exc:
        validate_transition(TaskState.COMPLETED, TaskState.RUNNING)
    assert exc.value.code == "INVALID_TASK_TRANSITION"

    with pytest.raises(InvalidTaskTransitionError):
        validate_transition(TaskState.FAILED, TaskState.QUEUED)

    with pytest.raises(InvalidTaskTransitionError):
        validate_transition(TaskState.CANCELLED, TaskState.RUNNING)

    # Cannot skip directly from Created to Completed
    with pytest.raises(InvalidTaskTransitionError):
        validate_transition(TaskState.CREATED, TaskState.COMPLETED)

    # Cannot transition Queued directly to Completed without Running
    with pytest.raises(InvalidTaskTransitionError):
        validate_transition(TaskState.QUEUED, TaskState.COMPLETED)
