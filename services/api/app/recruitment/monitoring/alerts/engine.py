"""Alert Rules Evaluation Engine for Stage 30 Recruitment Monitoring."""

from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import Any, Optional
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    RecruitmentAlertEventModel,
    RecruitmentAlertRuleModel,
    RecruitmentNotificationOutboxModel,
)
from app.recruitment.monitoring.alerts.grouping import cooldown_tracker
from app.recruitment.monitoring.contracts import (
    AlertEventData,
    AlertRuleCreateRequest,
    AlertRuleData,
    AlertRuleUpdateRequest,
    AlertSeverity,
    AlertTriggerType,
    NotificationDeliveryStatus,
)
from app.recruitment.monitoring.errors import AlertEventNotFoundError, AlertRuleNotFoundError

logger = logging.getLogger("autonom.recruitment.monitoring.alerts.engine")


class AlertEngine:
    """Manages alert rules, evaluates opportunities against triggers, and creates durable alerts and outbox notifications."""

    # -------------------------------------------------------------------------
    # Alert Rules
    # -------------------------------------------------------------------------

    async def create_rule(
        self,
        owner_id: str,
        req: AlertRuleCreateRequest,
        session: AsyncSession,
    ) -> AlertRuleData:
        rule = RecruitmentAlertRuleModel(
            owner_id=owner_id,
            name=req.name,
            profile_id=req.profile_id,
            watch_id=req.watch_id,
            trigger_type=req.trigger_type.value,
            conditions_json=req.conditions,
            delivery_channels_json=req.delivery_channels,
            quiet_hours_enabled=req.quiet_hours_enabled,
            cooldown_minutes=req.cooldown_minutes,
            enabled=True,
            version=1,
        )
        session.add(rule)
        await session.flush()
        return self._to_rule_data(rule)

    async def get_rule(self, rule_id: str, session: AsyncSession) -> AlertRuleData:
        stmt = select(RecruitmentAlertRuleModel).where(RecruitmentAlertRuleModel.id == rule_id)
        res = await session.execute(stmt)
        rule = res.scalar_one_or_none()
        if not rule:
            raise AlertRuleNotFoundError(f"Alert rule '{rule_id}' not found.")
        return self._to_rule_data(rule)

    async def list_rules(self, owner_id: str, session: AsyncSession) -> list[AlertRuleData]:
        stmt = select(RecruitmentAlertRuleModel).where(RecruitmentAlertRuleModel.owner_id == owner_id)
        res = await session.execute(stmt)
        items = list(res.scalars().all())
        return [self._to_rule_data(r) for r in items]

    async def update_rule(
        self,
        rule_id: str,
        req: AlertRuleUpdateRequest,
        session: AsyncSession,
    ) -> AlertRuleData:
        stmt = select(RecruitmentAlertRuleModel).where(RecruitmentAlertRuleModel.id == rule_id)
        res = await session.execute(stmt)
        rule = res.scalar_one_or_none()
        if not rule:
            raise AlertRuleNotFoundError(f"Alert rule '{rule_id}' not found.")

        if req.name is not None:
            rule.name = req.name
        if req.trigger_type is not None:
            rule.trigger_type = req.trigger_type.value
        if req.conditions is not None:
            rule.conditions_json = req.conditions
        if req.delivery_channels is not None:
            rule.delivery_channels_json = req.delivery_channels
        if req.quiet_hours_enabled is not None:
            rule.quiet_hours_enabled = req.quiet_hours_enabled
        if req.cooldown_minutes is not None:
            rule.cooldown_minutes = req.cooldown_minutes
        if req.enabled is not None:
            rule.enabled = req.enabled

        rule.version += 1
        rule.updated_at = datetime.now(UTC)
        await session.flush()
        return self._to_rule_data(rule)

    # -------------------------------------------------------------------------
    # Evaluation and Alert Creation
    # -------------------------------------------------------------------------

    async def evaluate_and_emit(
        self,
        owner_id: str,
        trigger_type: AlertTriggerType,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        canonical_job_id: Optional[str] = None,
        queue_entry_id: Optional[str] = None,
        run_id: Optional[str] = None,
        deep_link: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> Optional[AlertEventData]:
        """Evaluates triggers, deduplicates against cooldown, and creates persistent alert + outbox."""
        if not session:
            return None

        # Fingerprint check
        fp = cooldown_tracker.get_fingerprint(
            owner_id=owner_id,
            alert_type=trigger_type.value,
            canonical_job_id=canonical_job_id,
        )
        if cooldown_tracker.should_suppress(fp, cooldown_minutes=30):
            logger.info(f"Alert suppressed by cooldown: '{title}'")
            return None

        cooldown_tracker.record_alert(fp)

        # Create alert event
        event = RecruitmentAlertEventModel(
            owner_id=owner_id,
            queue_entry_id=queue_entry_id,
            canonical_job_id=canonical_job_id,
            run_id=run_id,
            title=title,
            message=message,
            alert_type=trigger_type.value,
            severity=severity.value,
            is_read=False,
            is_dismissed=False,
            deep_link=deep_link or f"/recruitment/monitoring",
            event_fingerprint=fp,
        )
        session.add(event)
        await session.flush()

        # Enqueue in-app and desktop notification outbox records
        for channel in ("in_app", "windows_desktop"):
            outbox = RecruitmentNotificationOutboxModel(
                alert_event_id=event.id,
                delivery_channel=channel,
                title=title,
                body=message,
                status=NotificationDeliveryStatus.READY.value,
                attempts=0,
            )
            session.add(outbox)

        await session.flush()
        return self._to_event_data(event)

    async def list_alerts(
        self,
        owner_id: str,
        session: AsyncSession,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AlertEventData]:
        stmt = select(RecruitmentAlertEventModel).where(RecruitmentAlertEventModel.owner_id == owner_id)
        if unread_only:
            stmt = stmt.where(RecruitmentAlertEventModel.is_read == False)

        stmt = stmt.order_by(RecruitmentAlertEventModel.created_at.desc()).limit(limit).offset(offset)
        res = await session.execute(stmt)
        items = list(res.scalars().all())
        return [self._to_event_data(e) for e in items]

    async def acknowledge_alert(self, alert_id: str, session: AsyncSession) -> bool:
        stmt = (
            update(RecruitmentAlertEventModel)
            .where(RecruitmentAlertEventModel.id == alert_id)
            .values(is_read=True, acknowledged_at=datetime.now(UTC))
        )
        res = await session.execute(stmt)
        await session.flush()
        return res.rowcount > 0

    async def dismiss_alert(self, alert_id: str, session: AsyncSession) -> bool:
        stmt = (
            update(RecruitmentAlertEventModel)
            .where(RecruitmentAlertEventModel.id == alert_id)
            .values(is_dismissed=True, is_read=True)
        )
        res = await session.execute(stmt)
        await session.flush()
        return res.rowcount > 0

    def _to_rule_data(self, r: RecruitmentAlertRuleModel) -> AlertRuleData:
        return AlertRuleData(
            id=r.id,
            owner_id=r.owner_id,
            name=r.name,
            profile_id=r.profile_id,
            watch_id=r.watch_id,
            trigger_type=AlertTriggerType(r.trigger_type),
            conditions=r.conditions_json or {},
            delivery_channels=r.delivery_channels_json or ["in_app"],
            quiet_hours_enabled=r.quiet_hours_enabled,
            cooldown_minutes=r.cooldown_minutes,
            enabled=r.enabled,
            version=r.version,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )

    def _to_event_data(self, e: RecruitmentAlertEventModel) -> AlertEventData:
        return AlertEventData(
            id=e.id,
            owner_id=e.owner_id,
            rule_id=e.rule_id,
            queue_entry_id=e.queue_entry_id,
            canonical_job_id=e.canonical_job_id,
            run_id=e.run_id,
            title=e.title,
            message=e.message,
            alert_type=AlertTriggerType(e.alert_type),
            severity=AlertSeverity(e.severity),
            is_read=e.is_read,
            is_dismissed=e.is_dismissed,
            acknowledged_at=e.acknowledged_at,
            deep_link=e.deep_link,
            created_at=e.created_at,
        )


alert_engine = AlertEngine()
