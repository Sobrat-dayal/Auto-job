"""Validation engine for Job Watches and Monitoring Profiles."""

from __future__ import annotations

import zoneinfo
from typing import Any
from app.recruitment.monitoring.contracts import (
    JobWatchCreateRequest,
    MonitoringProfileCreateRequest,
    ScheduleConfig,
)
from app.recruitment.monitoring.errors import (
    ProfileValidationError,
    ScheduleValidationError,
    WatchValidationError,
)


def validate_timezone(tz_name: str) -> None:
    """Verifies that the provided timezone name is a recognized IANA identifier."""
    if not tz_name:
        raise ScheduleValidationError("Timezone must not be empty.")
    try:
        zoneinfo.ZoneInfo(tz_name)
    except Exception as exc:
        raise ScheduleValidationError(f"Invalid IANA timezone: '{tz_name}'.") from exc


def validate_schedule_config(schedule: ScheduleConfig) -> None:
    """Enforces schedule constraints: minimum polling frequency (>= 5 mins), valid timezones."""
    validate_timezone(schedule.timezone)

    if schedule.recurrence_type.value == "interval":
        if schedule.interval_minutes < 5:
            raise ScheduleValidationError(
                f"Polling interval ({schedule.interval_minutes}m) violates minimum 5-minute safety threshold."
            )
        if schedule.interval_minutes > 10080:  # 7 days
            raise ScheduleValidationError("Polling interval cannot exceed 7 days (10080 minutes).")

    if schedule.recurrence_type.value in ("daily", "weekdays", "weekly", "selected_days"):
        time_parts = (schedule.time_of_day or "09:00").split(":")
        if len(time_parts) != 2:
            raise ScheduleValidationError("time_of_day must be in 'HH:MM' 24-hour format.")
        try:
            h, m = int(time_parts[0]), int(time_parts[1])
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError()
        except Exception as exc:
            raise ScheduleValidationError("Invalid hour or minute in time_of_day.") from exc


def validate_watch_request(req: JobWatchCreateRequest) -> None:
    """Validates complete watch parameters before activation."""
    if not req.name or len(req.name.strip()) < 2:
        raise WatchValidationError("Watch name must be at least 2 characters long.")

    if not req.approved_sources and not req.employer_ids and not req.career_strategy_id:
        raise WatchValidationError(
            "Watch must define at least one approved source, employer ID, or career strategy."
        )

    validate_schedule_config(req.schedule_config)


def validate_profile_request(req: MonitoringProfileCreateRequest) -> None:
    """Validates monitoring profile parameters."""
    if not req.name or len(req.name.strip()) < 2:
        raise ProfileValidationError("Profile name must be at least 2 characters long.")

    if req.retention_days < 7:
        raise ProfileValidationError("Retention period must be at least 7 days.")
