"""Schedule preview generator."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Optional
from app.recruitment.monitoring.contracts import (
    ScheduleConfig,
    SchedulePreviewOccurrence,
    SchedulePreviewResponse,
)
from app.recruitment.monitoring.scheduling.quiet_hours import is_in_quiet_hours
from app.recruitment.monitoring.scheduling.recurrence import calculate_upcoming_occurrences


def generate_schedule_preview(
    watch_name: str,
    schedule: ScheduleConfig,
    source_count: int = 1,
    start_time: Optional[datetime] = None,
    requires_authorization: bool = False,
) -> SchedulePreviewResponse:
    """Generates a non-executing preview of upcoming schedule occurrences and budget estimates."""
    base_time = start_time or datetime.now(UTC)
    upcoming_times = calculate_upcoming_occurrences(schedule, count=5, start_time=base_time)

    occurrences: list[SchedulePreviewOccurrence] = []
    quiet_hours_active_in_preview = False

    for idx, dt in enumerate(upcoming_times, start=1):
        in_qh = is_in_quiet_hours(schedule.quiet_hours, dt, schedule.timezone)
        if in_qh:
            quiet_hours_active_in_preview = True

        action = "execute"
        if in_qh:
            if schedule.quiet_hours.pause_source_monitoring:
                action = "skip_source_monitoring"
            elif schedule.quiet_hours.mute_notifications:
                action = "defer_notifications"

        occurrences.append(
            SchedulePreviewOccurrence(
                occurrence_index=idx,
                scheduled_time=dt,
                is_quiet_hours=in_qh,
                action=action,
            )
        )

    # Estimate budget: roughly 2-5 HTTP requests per source per run
    est_requests = max(1, source_count) * 3

    return SchedulePreviewResponse(
        watch_name=watch_name,
        timezone=schedule.timezone,
        recurrence_summary=f"{schedule.recurrence_type.value} (every {schedule.interval_minutes}m)"
        if schedule.recurrence_type.value == "interval"
        else f"{schedule.recurrence_type.value} at {schedule.time_of_day or '09:00'}",
        next_occurrences=occurrences,
        estimated_request_budget_per_run=est_requests,
        quiet_hours_active_in_preview=quiet_hours_active_in_preview,
        requires_authorization=requires_authorization,
    )
