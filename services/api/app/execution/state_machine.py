"""Task state machine transition rules and validator."""

from app.core.exceptions import InvalidTaskTransitionError
from app.schemas.tasks import TaskState

# Define valid state transitions based on AUTONOM architecture
VALID_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.CREATED: {
        TaskState.QUEUED,
        TaskState.CANCELLED,
    },
    TaskState.QUEUED: {
        TaskState.PLANNING,
        TaskState.RUNNING,
        TaskState.CANCELLED,
    },
    TaskState.PLANNING: {
        TaskState.RUNNING,
        TaskState.WAITING_FOR_DEPENDENCIES,
        TaskState.CANCELLED,
        TaskState.FAILED,
    },
    TaskState.WAITING_FOR_DEPENDENCIES: {
        TaskState.RUNNING,
        TaskState.CANCELLED,
        TaskState.FAILED,
    },
    TaskState.RUNNING: {
        TaskState.WAITING_FOR_AUTHORIZATION,
        TaskState.PAUSED,
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.CANCELLED,
        TaskState.RETRYING,
    },
    TaskState.WAITING_FOR_AUTHORIZATION: {
        TaskState.RUNNING,
        TaskState.CANCELLED,
        TaskState.FAILED,
    },
    TaskState.PAUSED: {
        TaskState.RUNNING,
        TaskState.CANCELLED,
    },
    TaskState.RETRYING: {
        TaskState.QUEUED,
        TaskState.RUNNING,
        TaskState.FAILED,
        TaskState.CANCELLED,
    },
    # Terminal states have no valid outgoing transitions
    TaskState.COMPLETED: set(),
    TaskState.FAILED: set(),
    TaskState.CANCELLED: set(),
}


def validate_transition(
    current_state: TaskState,
    target_state: TaskState,
    task_id: str | None = None,
) -> None:
    """Enforces valid task state transitions, raising InvalidTaskTransitionError on illegal shifts."""
    if current_state == target_state:
        return

    allowed = VALID_TRANSITIONS.get(current_state, set())
    if target_state not in allowed:
        raise InvalidTaskTransitionError(
            current_state=current_state.value,
            target_state=target_state.value,
            task_id=task_id,
        )
