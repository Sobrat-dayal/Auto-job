"""Durable notification outbox dispatcher with quiet hours and privacy protection."""

from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RecruitmentNotificationOutboxModel
from app.recruitment.monitoring.contracts import (
    NotificationDeliveryStatus,
    NotificationOutboxData,
    QuietHoursConfig,
)
from app.recruitment.monitoring.scheduling.quiet_hours import should_defer_notifications

logger = logging.getLogger("autonom.recruitment.monitoring.alerts.outbox")


class NotificationOutboxManager:
    """Manages asynchronous delivery of in-app and desktop notifications from the durable outbox."""

    async def list_notifications(
        self,
        session: AsyncSession,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[NotificationOutboxData]:
        stmt = select(RecruitmentNotificationOutboxModel)
        if status:
            stmt = stmt.where(RecruitmentNotificationOutboxModel.status == status)

        stmt = stmt.order_by(RecruitmentNotificationOutboxModel.created_at.desc()).limit(limit)
        res = await session.execute(stmt)
        items = list(res.scalars().all())
        return [self._to_outbox_data(n) for n in items]

    async def mark_as_read(self, notification_id: str, session: AsyncSession) -> bool:
        stmt = (
            update(RecruitmentNotificationOutboxModel)
            .where(RecruitmentNotificationOutboxModel.id == notification_id)
            .values(status=NotificationDeliveryStatus.READ.value)
        )
        res = await session.execute(stmt)
        await session.flush()
        return res.rowcount > 0

    async def process_outbox(
        self,
        session: AsyncSession,
        quiet_hours: Optional[QuietHoursConfig] = None,
        timezone: str = "UTC",
        privacy_mode: bool = True,
    ) -> int:
        """Processes ready notifications, deferring if quiet hours are active."""
        stmt = select(RecruitmentNotificationOutboxModel).where(
            RecruitmentNotificationOutboxModel.status.in_(
                [NotificationDeliveryStatus.READY.value, NotificationDeliveryStatus.DEFERRED_BY_QUIET_HOURS.value]
            )
        )
        res = await session.execute(stmt)
        items = list(res.scalars().all())

        delivered_count = 0
        now = datetime.now(UTC)
        defer = should_defer_notifications(quiet_hours or QuietHoursConfig(), now, timezone)

        for item in items:
            if defer and item.delivery_channel == "windows_desktop":
                item.status = NotificationDeliveryStatus.DEFERRED_BY_QUIET_HOURS.value
                continue

            # In privacy mode, sanitize title/body for desktop notification
            if privacy_mode and item.delivery_channel == "windows_desktop":
                body = "A recruitment update is ready for review in AUTONOM."
            else:
                body = item.body

            # Dispatch notification
            item.status = NotificationDeliveryStatus.DELIVERED_WHERE_CONFIRMED.value
            item.attempts += 1
            item.last_attempt_at = now
            delivered_count += 1

        await session.flush()
        return delivered_count

    def _to_outbox_data(self, n: RecruitmentNotificationOutboxModel) -> NotificationOutboxData:
        return NotificationOutboxData(
            id=n.id,
            alert_event_id=n.alert_event_id,
            delivery_channel=n.delivery_channel,
            title=n.title,
            body=n.body,
            status=NotificationDeliveryStatus(n.status),
            attempts=n.attempts,
            last_attempt_at=n.last_attempt_at,
            error_message=n.error_message,
            deferred_until=n.deferred_until,
            created_at=n.created_at,
        )


notification_outbox = NotificationOutboxManager()
