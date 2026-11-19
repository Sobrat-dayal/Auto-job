"""Quiet hours evaluator supporting timezone conversion and cross-midnight boundaries."""

from __future__ import annotations

from datetime import UTC, datetime, time
import zoneinfo
from typing import Optional
from app.recruitment.monitoring.contracts import QuietHoursConfig


def is_in_quiet_hours(
    quiet_hours: QuietHoursConfig,
    check_time_utc: Optional[datetime] = None,
    tz_name: str = "UTC",
) -> bool:
    """Checks whether the specified UTC time falls within the configured quiet hours in local time."""
    if not quiet_hours.enabled:
        return False

    try:
        tz = zoneinfo.ZoneInfo(tz_name)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    dt_utc = check_time_utc or datetime.now(UTC)
    dt_local = dt_utc.astimezone(tz)
    current_time = dt_local.time()

    # Parse start and end times
    try:
        sh, sm = [int(p) for p in quiet_hours.start_time.split(":")[:2]]
        eh, em = [int(p) for p in quiet_hours.end_time.split(":")[:2]]
        start = time(sh, sm)
        end = time(eh, em)
    except Exception:
        # Default 22:00 to 08:00
        start = time(22, 0)
        end = time(8, 0)

    if start < end:
        # Same day interval (e.g. 01:00 to 06:00)
        return start <= current_time <= end
    else:
        # Crosses midnight (e.g. 22:00 to 08:00)
        return current_time >= start or current_time <= end


def should_defer_notifications(
    quiet_hours: QuietHoursConfig,
    check_time_utc: Optional[datetime] = None,
    tz_name: str = "UTC",
) -> bool:
    """Returns True if notifications should be deferred/muted right now."""
    if not quiet_hours.mute_notifications:
        return False
    return is_in_quiet_hours(quiet_hours, check_time_utc, tz_name)


def should_pause_monitoring(
    quiet_hours: QuietHoursConfig,
    check_time_utc: Optional[datetime] = None,
    tz_name: str = "UTC",
) -> bool:
    """Returns True if source network monitoring itself should be paused during quiet hours."""
    if not quiet_hours.pause_source_monitoring:
        return False
    return is_in_quiet_hours(quiet_hours, check_time_utc, tz_name)
