"""Tests for Stage 30 schedule calculations, recurrence, timezone handling, and missed runs."""

from datetime import UTC, datetime, timedelta
import zoneinfo
import pytest

from app.recruitment.monitoring.contracts import (
    MissedRunPolicy,
    QuietHoursConfig,
    RecurrenceType,
    ScheduleConfig,
)
from app.recruitment.monitoring.scheduling.missed_runs import evaluate_missed_run
from app.recruitment.monitoring.scheduling.preview import generate_schedule_preview
from app.recruitment.monitoring.scheduling.quiet_hours import is_in_quiet_hours
from app.recruitment.monitoring.scheduling.recurrence import (
    calculate_next_occurrence,
    calculate_upcoming_occurrences,
    get_zoneinfo,
)


def test_get_zoneinfo():
    tz = get_zoneinfo("America/New_York")
    assert tz.key == "America/New_York"
    fallback_tz = get_zoneinfo("Invalid/NonExistent_Zone")
    assert fallback_tz.key == "UTC"


def test_interval_recurrence_calculation():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=30,
        timezone="UTC",
    )
    base = datetime(2026, 6, 1, 10, 0, 0, tzinfo=UTC)
    next_time = calculate_next_occurrence(schedule, after_time=base)
    assert next_time == datetime(2026, 6, 1, 10, 30, 0, tzinfo=UTC)


def test_interval_recurrence_enforces_5min_minimum():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ScheduleConfig(
            recurrence_type=RecurrenceType.INTERVAL,
            interval_minutes=1,  # Below 5m bound
            timezone="UTC",
        )
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=5,
        timezone="UTC",
    )
    base = datetime(2026, 6, 1, 10, 0, 0, tzinfo=UTC)
    next_time = calculate_next_occurrence(schedule, after_time=base)
    assert next_time == datetime(2026, 6, 1, 10, 5, 0, tzinfo=UTC)


def test_daily_recurrence_calculation():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.DAILY,
        time_of_day="14:00",
        timezone="UTC",
    )
    # Morning before 14:00 -> should trigger same day at 14:00
    base_morning = datetime(2026, 6, 1, 9, 30, 0, tzinfo=UTC)
    next_time = calculate_next_occurrence(schedule, after_time=base_morning)
    assert next_time == datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)

    # Afternoon after 14:00 -> should trigger next day at 14:00
    base_afternoon = datetime(2026, 6, 1, 15, 0, 0, tzinfo=UTC)
    next_time_tomorrow = calculate_next_occurrence(schedule, after_time=base_afternoon)
    assert next_time_tomorrow == datetime(2026, 6, 2, 14, 0, 0, tzinfo=UTC)


def test_weekdays_recurrence_skips_weekends():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.WEEKDAYS,
        time_of_day="09:00",
        timezone="UTC",
    )
    # Friday evening (2026-06-05 is Friday)
    friday_night = datetime(2026, 6, 5, 20, 0, 0, tzinfo=UTC)
    next_time = calculate_next_occurrence(schedule, after_time=friday_night)
    # Must jump past Saturday (6th) and Sunday (7th) to Monday June 8th 09:00
    assert next_time == datetime(2026, 6, 8, 9, 0, 0, tzinfo=UTC)
    assert next_time.weekday() == 0  # Monday


def test_weekly_recurrence_specific_days():
    # Target Wednesdays (weekday index 2)
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.WEEKLY,
        time_of_day="10:00",
        days_of_week=[2],
        timezone="UTC",
    )
    # Monday June 1st, 2026
    base_monday = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
    next_time = calculate_next_occurrence(schedule, after_time=base_monday)
    # Wednesday is June 3rd
    assert next_time == datetime(2026, 6, 3, 10, 0, 0, tzinfo=UTC)


def test_calculate_upcoming_occurrences():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=15,
        timezone="UTC",
    )
    base = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
    upcoming = calculate_upcoming_occurrences(schedule, count=3, start_time=base)
    assert len(upcoming) == 3
    assert upcoming[0] == datetime(2026, 6, 1, 12, 15, 0, tzinfo=UTC)
    assert upcoming[1] == datetime(2026, 6, 1, 12, 30, 0, tzinfo=UTC)
    assert upcoming[2] == datetime(2026, 6, 1, 12, 45, 0, tzinfo=UTC)


def test_missed_run_policy_skip():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=60,
        missed_run_policy=MissedRunPolicy.SKIP,
    )
    now = datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)
    due_at = datetime(2026, 6, 1, 10, 0, 0, tzinfo=UTC)  # 4 hours late
    decision = evaluate_missed_run(schedule, last_run_at=None, scheduled_due_at=due_at, current_time=now)
    assert decision.action == "skip"
    assert "skipped per policy" in decision.reason


def test_missed_run_policy_run_latest():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=60,
        missed_run_policy=MissedRunPolicy.RUN_LATEST_DUE,
    )
    now = datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)
    due_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
    decision = evaluate_missed_run(schedule, last_run_at=None, scheduled_due_at=due_at, current_time=now)
    assert decision.action == "execute_latest"


def test_missed_run_excessive_delay_requires_review():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=60,
        missed_run_policy=MissedRunPolicy.RUN_LATEST_DUE,
    )
    now = datetime(2026, 6, 15, 14, 0, 0, tzinfo=UTC)
    due_at = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)  # 14 days ago
    decision = evaluate_missed_run(schedule, last_run_at=None, scheduled_due_at=due_at, current_time=now)
    assert decision.action == "require_review"


def test_schedule_preview_generation():
    schedule = ScheduleConfig(
        recurrence_type=RecurrenceType.INTERVAL,
        interval_minutes=30,
        timezone="UTC",
        quiet_hours=QuietHoursConfig(
            enabled=True,
            start_time="22:00",
            end_time="07:00",
            pause_source_monitoring=True,
        ),
    )
    start = datetime(2026, 6, 1, 21, 45, 0, tzinfo=UTC)
    preview = generate_schedule_preview("Test Watch", schedule, source_count=2, start_time=start)
    assert preview.watch_name == "Test Watch"
    assert len(preview.next_occurrences) == 5
    assert preview.estimated_request_budget_per_run == 6
    # Occurrence 1 at 22:15 should be marked quiet hours and skip_source_monitoring
    assert preview.next_occurrences[0].is_quiet_hours is True
    assert preview.next_occurrences[0].action == "skip_source_monitoring"
