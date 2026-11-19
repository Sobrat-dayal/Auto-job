"""Tests for Stage 30 Alert Engine, rules, cooldown deduplication, and notification outbox."""

from datetime import UTC, datetime
import pytest

from app.db.engine import async_session_factory
from app.recruitment.monitoring.alerts.engine import AlertEngine
from app.recruitment.monitoring.alerts.grouping import cooldown_tracker
from app.recruitment.monitoring.alerts.outbox import NotificationOutboxManager
from app.recruitment.monitoring.contracts import (
    AlertRuleCreateRequest,
    AlertSeverity,
    AlertTriggerType,
    NotificationDeliveryStatus,
    QuietHoursConfig,
)


@pytest.mark.asyncio
async def test_alert_rule_lifecycle():
    engine = AlertEngine()
    req = AlertRuleCreateRequest(
        name="High Match Alert",
        trigger_type=AlertTriggerType.HIGH_PRIORITY_JOB,
        conditions={"min_score": 85.0},
        delivery_channels=["in_app", "windows_desktop"],
        quiet_hours_enabled=True,
        cooldown_minutes=60,
    )

    async with async_session_factory() as session:
        created = await engine.create_rule(owner_id="test_user", req=req, session=session)
        assert created.name == "High Match Alert"
        assert created.trigger_type == AlertTriggerType.HIGH_PRIORITY_JOB
        assert created.enabled is True

        fetched = await engine.get_rule(created.id, session=session)
        assert fetched.id == created.id
        assert fetched.conditions.get("min_score") == 85.0


@pytest.mark.asyncio
async def test_alert_emission_and_cooldown_dedup():
    engine = AlertEngine()
    cooldown_tracker.clear()  # reset state

    async with async_session_factory() as session:
        # First alert emits successfully
        evt1 = await engine.evaluate_and_emit(
            owner_id="test_user",
            trigger_type=AlertTriggerType.HIGH_PRIORITY_JOB,
            title="Exciting Opportunity at Acme",
            message="Your match score is 94%!",
            severity=AlertSeverity.INFO,
            canonical_job_id="job_alert_test_01",
            session=session,
        )
        assert evt1 is not None
        assert evt1.title == "Exciting Opportunity at Acme"

        # Immediate duplicate alert with same fingerprint is suppressed by cooldown
        evt2 = await engine.evaluate_and_emit(
            owner_id="test_user",
            trigger_type=AlertTriggerType.HIGH_PRIORITY_JOB,
            title="Exciting Opportunity at Acme (dup)",
            message="Your match score is 94%!",
            severity=AlertSeverity.INFO,
            canonical_job_id="job_alert_test_01",
            session=session,
        )
        assert evt2 is None

        # Different job ID emits successfully
        evt3 = await engine.evaluate_and_emit(
            owner_id="test_user",
            trigger_type=AlertTriggerType.HIGH_PRIORITY_JOB,
            title="Exciting Opportunity at Beta Corp",
            message="Your match score is 91%!",
            severity=AlertSeverity.INFO,
            canonical_job_id="job_alert_test_02",
            session=session,
        )
        assert evt3 is not None


@pytest.mark.asyncio
async def test_alert_acknowledgement_and_dismissal():
    engine = AlertEngine()
    cooldown_tracker.clear()

    async with async_session_factory() as session:
        evt = await engine.evaluate_and_emit(
            owner_id="user_ack_test",
            trigger_type=AlertTriggerType.JOB_CLOSED,
            title="Role Status Updated",
            message="Role was marked closed",
            severity=AlertSeverity.INFO,
            canonical_job_id="job_ack_01",
            session=session,
        )
        assert evt is not None
        assert evt.is_read is False

        # Acknowledge
        acked = await engine.acknowledge_alert(evt.id, session=session)
        assert acked is True

        # Dismiss
        dismissed = await engine.dismiss_alert(evt.id, session=session)
        assert dismissed is True


@pytest.mark.asyncio
async def test_notification_outbox_processing_and_quiet_hours():
    engine = AlertEngine()
    outbox_mgr = NotificationOutboxManager()
    cooldown_tracker.clear()

    async with async_session_factory() as session:
        evt = await engine.evaluate_and_emit(
            owner_id="user_outbox_test",
            trigger_type=AlertTriggerType.APPROACHING_DEADLINE,
            title="Application Deadline in 24h",
            message="Apply before midnight tomorrow",
            severity=AlertSeverity.CRITICAL,
            canonical_job_id="job_deadline_01",
            session=session,
        )
        assert evt is not None

        # Process outbox outside quiet hours
        qh_disabled = QuietHoursConfig(enabled=False)
        delivered_count = await outbox_mgr.process_outbox(
            session=session,
            quiet_hours=qh_disabled,
            privacy_mode=True,
        )
        assert delivered_count >= 1
