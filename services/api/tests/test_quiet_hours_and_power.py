"""Tests for Quiet Hours evaluation across midnight and Windows lifecycle management."""

from datetime import UTC, datetime
import pytest

from app.recruitment.monitoring.contracts import (
    MonitoringSettingsUpdateRequest,
    QuietHoursConfig,
)
from app.recruitment.monitoring.platform.windows_lifecycle import WindowsLifecycleManager
from app.recruitment.monitoring.scheduling.quiet_hours import (
    is_in_quiet_hours,
    should_defer_notifications,
    should_pause_monitoring,
)


def test_quiet_hours_disabled():
    qh = QuietHoursConfig(enabled=False, start_time="22:00", end_time="08:00")
    # Midnight in UTC
    dt = datetime(2026, 6, 1, 0, 30, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt, tz_name="UTC") is False


def test_quiet_hours_cross_midnight_inside():
    # 22:00 to 08:00
    qh = QuietHoursConfig(
        enabled=True,
        start_time="22:00",
        end_time="08:00",
        mute_notifications=True,
        pause_source_monitoring=True,
    )
    # 23:30 is inside
    dt_late = datetime(2026, 6, 1, 23, 30, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_late, tz_name="UTC") is True
    assert should_defer_notifications(qh, dt_late, tz_name="UTC") is True
    assert should_pause_monitoring(qh, dt_late, tz_name="UTC") is True

    # 03:15 is inside
    dt_early = datetime(2026, 6, 2, 3, 15, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_early, tz_name="UTC") is True

    # 07:59 is inside
    dt_almost_end = datetime(2026, 6, 2, 7, 59, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_almost_end, tz_name="UTC") is True


def test_quiet_hours_cross_midnight_outside():
    qh = QuietHoursConfig(
        enabled=True,
        start_time="22:00",
        end_time="08:00",
    )
    # 12:00 noon is outside
    dt_noon = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_noon, tz_name="UTC") is False
    assert should_defer_notifications(qh, dt_noon, tz_name="UTC") is False
    assert should_pause_monitoring(qh, dt_noon, tz_name="UTC") is False

    # 21:50 is outside
    dt_evening = datetime(2026, 6, 1, 21, 50, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_evening, tz_name="UTC") is False


def test_quiet_hours_timezone_conversion():
    # 22:00 to 08:00 Eastern Time (UTC-4 in summer)
    qh = QuietHoursConfig(
        enabled=True,
        start_time="22:00",
        end_time="08:00",
    )
    # 03:00 UTC corresponds to 23:00 EDT (which is inside quiet hours)
    dt_utc = datetime(2026, 6, 2, 3, 0, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_utc, tz_name="America/New_York") is True

    # 18:00 UTC corresponds to 14:00 EDT (outside quiet hours)
    dt_utc_day = datetime(2026, 6, 2, 18, 0, 0, tzinfo=UTC)
    assert is_in_quiet_hours(qh, dt_utc_day, tz_name="America/New_York") is False


@pytest.mark.asyncio
async def test_windows_lifecycle_settings():
    from app.db.engine import async_session_factory
    mgr = WindowsLifecycleManager()

    async with async_session_factory() as session:
        settings_data = await mgr.get_settings(owner_id="test_user", session=session)
        assert settings_data.owner_id == "test_user"
        assert settings_data.background_monitoring_enabled is True

        # Update settings
        updated = await mgr.update_settings(
            owner_id="test_user",
            req=MonitoringSettingsUpdateRequest(
                default_interval_minutes=90,
                daily_request_budget=800,
                quiet_hours_start="23:00",
            ),
            session=session,
        )
        assert updated.default_interval_minutes == 90
        assert updated.daily_request_budget == 800
        assert updated.quiet_hours_start == "23:00"
