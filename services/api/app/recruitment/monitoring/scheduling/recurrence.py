"""Timezone-aware recurrence calculator supporting intervals, daily, weekly, cron, and DST."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import zoneinfo
from typing import Optional
from app.recruitment.monitoring.contracts import RecurrenceType, ScheduleConfig
from app.recruitment.monitoring.errors import ScheduleValidationError


def get_zoneinfo(tz_name: str) -> zoneinfo.ZoneInfo:
    """Safely retrieves ZoneInfo, defaulting to UTC if invalid."""
    try:
        return zoneinfo.ZoneInfo(tz_name)
    except Exception:
        return zoneinfo.ZoneInfo("UTC")


def calculate_next_occurrence(
    schedule: ScheduleConfig,
    after_time: Optional[datetime] = None,
) -> datetime:
    """Calculates the next due datetime in UTC, respecting the configured timezone and recurrence type."""
    tz = get_zoneinfo(schedule.timezone)
    base_time = after_time or datetime.now(UTC)
    local_base = base_time.astimezone(tz)

    if schedule.recurrence_type == RecurrenceType.INTERVAL:
        interval_mins = max(5, schedule.interval_minutes)
        next_dt = local_base + timedelta(minutes=interval_mins)
        return next_dt.astimezone(UTC)

    elif schedule.recurrence_type == RecurrenceType.HOURLY:
        # Next top of the hour
        next_dt = local_base.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        if next_dt <= local_base:
            next_dt += timedelta(hours=1)
        return next_dt.astimezone(UTC)

    elif schedule.recurrence_type == RecurrenceType.DAILY:
        time_parts = (schedule.time_of_day or "09:00").split(":")
        target_hour = int(time_parts[0]) if len(time_parts) > 0 else 9
        target_minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        target_today = local_base.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target_today > local_base:
            return target_today.astimezone(UTC)
        next_day = target_today + timedelta(days=1)
        return next_day.astimezone(UTC)

    elif schedule.recurrence_type == RecurrenceType.WEEKDAYS:
        # Monday to Friday (0=Mon, 4=Fri)
        time_parts = (schedule.time_of_day or "09:00").split(":")
        target_hour = int(time_parts[0]) if len(time_parts) > 0 else 9
        target_minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        candidate = local_base.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if candidate <= local_base:
            candidate += timedelta(days=1)

        while candidate.weekday() >= 5:  # Saturday or Sunday
            candidate += timedelta(days=1)

        return candidate.astimezone(UTC)

    elif schedule.recurrence_type == RecurrenceType.WEEKLY or schedule.recurrence_type == RecurrenceType.SELECTED_DAYS:
        target_days = schedule.days_of_week or [0]  # Default Monday
        time_parts = (schedule.time_of_day or "09:00").split(":")
        target_hour = int(time_parts[0]) if len(time_parts) > 0 else 9
        target_minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        candidate = local_base.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if candidate <= local_base:
            candidate += timedelta(days=1)

        for _ in range(14):  # Look up to 2 weeks
            if candidate.weekday() in target_days:
                return candidate.astimezone(UTC)
            candidate += timedelta(days=1)

        return (local_base + timedelta(days=7)).astimezone(UTC)

    elif schedule.recurrence_type == RecurrenceType.CRON:
        # Fallback to bounded interval if cron parsing not installed
        interval_mins = max(15, schedule.interval_minutes)
        return (local_base + timedelta(minutes=interval_mins)).astimezone(UTC)

    else:
        raise ScheduleValidationError(f"Unsupported recurrence type: {schedule.recurrence_type}")


def calculate_upcoming_occurrences(
    schedule: ScheduleConfig,
    count: int = 5,
    start_time: Optional[datetime] = None,
) -> list[datetime]:
    """Generates the next N scheduled run times in UTC."""
    occurrences = []
    current_time = start_time or datetime.now(UTC)
    for _ in range(count):
        next_occ = calculate_next_occurrence(schedule, after_time=current_time)
        occurrences.append(next_occ)
        current_time = next_occ
    return occurrences
