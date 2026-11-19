"""Tests for Emergency Stop integration blocking Stage 30 monitoring runs."""

import pytest
from app.db.engine import async_session_factory
from app.recruitment.monitoring.contracts import RunTriggerType
from app.recruitment.monitoring.errors import EmergencyStopActiveError
from app.recruitment.monitoring.execution.coordinator import MonitoringRunCoordinator
from app.security.authorization.emergency import EmergencyStopController


@pytest.mark.asyncio
async def test_emergency_stop_blocks_monitoring_execution():
    ctrl = EmergencyStopController.get_instance()
    coordinator = MonitoringRunCoordinator()

    # Activate emergency stop
    await ctrl.activate_emergency_stop(activated_by="admin", reason="Security Incident Test")
    assert ctrl.is_emergency_stop_active is True

    try:
        async with async_session_factory() as session:
            with pytest.raises(EmergencyStopActiveError) as exc_info:
                await coordinator.execute_run(
                    watch_id="non_existent_watch",
                    trigger_type=RunTriggerType.MANUAL,
                    worker_id="test_worker",
                    db_session=session,
                )
            assert "Emergency Stop" in str(exc_info.value)
    finally:
        # Reset emergency stop
        await ctrl.clear_emergency_stop(cleared_by="admin")
        assert ctrl.is_emergency_stop_active is False


@pytest.mark.asyncio
async def test_automation_pause_blocks_monitoring_execution():
    ctrl = EmergencyStopController.get_instance()
    coordinator = MonitoringRunCoordinator()

    # Pause automation
    await ctrl.pause_automation(paused_by="admin", reason="Maintenance Window")
    assert ctrl.is_automation_paused is True

    try:
        async with async_session_factory() as session:
            with pytest.raises(EmergencyStopActiveError) as exc_info:
                await coordinator.execute_run(
                    watch_id="non_existent_watch",
                    trigger_type=RunTriggerType.SCHEDULED,
                    worker_id="test_worker",
                    db_session=session,
                )
            assert "Automation Pause" in str(exc_info.value)
    finally:
        await ctrl.resume_automation(resumed_by="admin")
        assert ctrl.is_automation_paused is False
