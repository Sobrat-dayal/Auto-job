"""Missed scheduled run reconciliation policy evaluator."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Optional
from app.recruitment.monitoring.contracts import MissedRunPolicy, ScheduleConfig

logger = logging.getLogger("autonom.recruitment.monitoring.scheduling.missed_runs")


class MissedRunDecision:
    def __init__(self, action: str, reason: str, next_scheduled_time: datetime) -> None:
        self.action = action  # "execute_latest", "skip", "require_review"
        self.reason = reason
        self.next_scheduled_time = next_scheduled_time


def evaluate_missed_run(
    schedule: ScheduleConfig,
    last_run_at: Optional[datetime],
    scheduled_due_at: Optional[datetime],
    current_time: Optional[datetime] = None,
) -> MissedRunDecision:
    """Evaluates how to handle a scheduled run that was missed during suspension/downtime."""
    now = current_time or datetime.now(UTC)

    if not scheduled_due_at or scheduled_due_at > now:
        # Not missed
        from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
        return MissedRunDecision(
            action="normal",
            reason="Run is on schedule",
            next_scheduled_time=scheduled_due_at or calculate_next_occurrence(schedule, now),
        )

    delay = now - scheduled_due_at
    policy = schedule.missed_run_policy

    if delay > timedelta(days=7):
        logger.warning(f"Run missed by more than 7 days ({delay}). Requiring review.")
        from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
        return MissedRunDecision(
            action="require_review",
            reason=f"Significant elapsed time since last due run ({delay.days} days). Review recommended.",
            next_scheduled_time=calculate_next_occurrence(schedule, now),
        )

    if policy == MissedRunPolicy.SKIP:
        from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
        next_run = calculate_next_occurrence(schedule, now)
        return MissedRunDecision(
            action="skip",
            reason=f"Missed scheduled run at {scheduled_due_at.isoformat()} skipped per policy.",
            next_scheduled_time=next_run,
        )

    elif policy in (MissedRunPolicy.RUN_LATEST_DUE, MissedRunPolicy.RUN_ONCE_AFTER_RESTART):
        from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
        next_run = calculate_next_occurrence(schedule, now)
        return MissedRunDecision(
            action="execute_latest",
            reason=f"Executing single latest missed run from {scheduled_due_at.isoformat()}.",
            next_scheduled_time=next_run,
        )

    elif policy == MissedRunPolicy.REQUIRE_REVIEW:
        from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
        return MissedRunDecision(
            action="require_review",
            reason="Missed run requires manual user review per policy.",
            next_scheduled_time=calculate_next_occurrence(schedule, now),
        )

    from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
    return MissedRunDecision(
        action="execute_latest",
        reason="Defaulting to single missed run execution.",
        next_scheduled_time=calculate_next_occurrence(schedule, now),
    )
