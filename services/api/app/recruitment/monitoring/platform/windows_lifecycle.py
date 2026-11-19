"""Windows 11 background lifecycle, sleep/wake reconciliation, and startup integration."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    RecruitmentJobWatchModel,
    RecruitmentMonitoringSettingsModel,
    RecruitmentWorkerLeaseModel,
)
from app.recruitment.monitoring.contracts import (
    MonitoringSettingsData,
    MonitoringSettingsUpdateRequest,
    ScheduleConfig,
    WatchStatus,
)
from app.recruitment.monitoring.scheduling.missed_runs import evaluate_missed_run

logger = logging.getLogger("autonom.recruitment.monitoring.platform.windows_lifecycle")


class WindowsLifecycleManager:
    """Manages background monitoring state, Windows sleep/wake recovery, and desktop startup options."""

    def __init__(self) -> None:
        self._last_heartbeat_utc: datetime = datetime.now(UTC)
        self._is_suspended: bool = False

    async def get_settings(self, owner_id: str, session: AsyncSession) -> MonitoringSettingsData:
        stmt = select(RecruitmentMonitoringSettingsModel).where(
            RecruitmentMonitoringSettingsModel.owner_id == owner_id
        )
        res = await session.execute(stmt)
        s = res.scalar_one_or_none()

        if not s:
            s = RecruitmentMonitoringSettingsModel(
                owner_id=owner_id,
                background_monitoring_enabled=True,
                start_at_windows_signin=False,
                minimize_to_tray=True,
                default_interval_minutes=60,
                global_concurrency_limit=3,
                daily_request_budget=500,
                pause_on_battery=False,
                quiet_hours_enabled=True,
                quiet_hours_start="22:00",
                quiet_hours_end="08:00",
                timezone="UTC",
                notification_privacy_mode=True,
                retention_days=90,
            )
            session.add(s)
            await session.flush()

        return self._to_settings_data(s)

    async def update_settings(
        self,
        owner_id: str,
        req: MonitoringSettingsUpdateRequest,
        session: AsyncSession,
    ) -> MonitoringSettingsData:
        stmt = select(RecruitmentMonitoringSettingsModel).where(
            RecruitmentMonitoringSettingsModel.owner_id == owner_id
        )
        res = await session.execute(stmt)
        s = res.scalar_one_or_none()

        if not s:
            s = RecruitmentMonitoringSettingsModel(owner_id=owner_id)
            session.add(s)

        if req.background_monitoring_enabled is not None:
            s.background_monitoring_enabled = req.background_monitoring_enabled
        if req.start_at_windows_signin is not None:
            s.start_at_windows_signin = req.start_at_windows_signin
        if req.minimize_to_tray is not None:
            s.minimize_to_tray = req.minimize_to_tray
        if req.default_interval_minutes is not None:
            s.default_interval_minutes = req.default_interval_minutes
        if req.global_concurrency_limit is not None:
            s.global_concurrency_limit = req.global_concurrency_limit
        if req.daily_request_budget is not None:
            s.daily_request_budget = req.daily_request_budget
        if req.pause_on_battery is not None:
            s.pause_on_battery = req.pause_on_battery
        if req.quiet_hours_enabled is not None:
            s.quiet_hours_enabled = req.quiet_hours_enabled
        if req.quiet_hours_start is not None:
            s.quiet_hours_start = req.quiet_hours_start
        if req.quiet_hours_end is not None:
            s.quiet_hours_end = req.quiet_hours_end
        if req.timezone is not None:
            s.timezone = req.timezone
        if req.notification_privacy_mode is not None:
            s.notification_privacy_mode = req.notification_privacy_mode
        if req.retention_days is not None:
            s.retention_days = req.retention_days

        s.updated_at = datetime.now(UTC)
        await session.flush()
        return self._to_settings_data(s)

    async def reconcile_after_wake(self, session: AsyncSession) -> dict[str, Any]:
        """Detects elapsed sleep time, reconciles missed watch occurrences, and purges dead worker leases."""
        now = datetime.now(UTC)
        elapsed = now - self._last_heartbeat_utc
        self._last_heartbeat_utc = now

        logger.info(f"Reconciling monitoring state after potential sleep. Elapsed: {elapsed}")

        # Purge stale worker leases held prior to sleep
        purge_stmt = select(RecruitmentWorkerLeaseModel).where(RecruitmentWorkerLeaseModel.expires_at < now)
        res = await session.execute(purge_stmt)
        expired_leases = list(res.scalars().all())
        for lease in expired_leases:
            await session.delete(lease)

        # Inspect active watches and reconcile due times
        stmt_w = select(RecruitmentJobWatchModel).where(
            RecruitmentJobWatchModel.status == WatchStatus.ACTIVE.value
        )
        res_w = await session.execute(stmt_w)
        active_watches = list(res_w.scalars().all())

        reconciled_count = 0
        for w in active_watches:
            if w.next_due_run_at and w.next_due_run_at < now:
                sched = ScheduleConfig(**(w.schedule_config_json or {}))
                decision = evaluate_missed_run(
                    schedule=sched,
                    last_run_at=w.last_run_at,
                    scheduled_due_at=w.next_due_run_at,
                    current_time=now,
                )
                w.next_due_run_at = decision.next_scheduled_time
                reconciled_count += 1

        await session.flush()
        return {
            "elapsed_seconds": int(elapsed.total_seconds()),
            "expired_leases_purged": len(expired_leases),
            "reconciled_watches_count": reconciled_count,
            "reconciled_at": now.isoformat(),
        }

    def _to_settings_data(self, s: RecruitmentMonitoringSettingsModel) -> MonitoringSettingsData:
        return MonitoringSettingsData(
            owner_id=s.owner_id,
            background_monitoring_enabled=s.background_monitoring_enabled,
            start_at_windows_signin=s.start_at_windows_signin,
            minimize_to_tray=s.minimize_to_tray,
            default_interval_minutes=s.default_interval_minutes,
            global_concurrency_limit=s.global_concurrency_limit,
            daily_request_budget=s.daily_request_budget,
            pause_on_battery=s.pause_on_battery,
            quiet_hours_enabled=s.quiet_hours_enabled,
            quiet_hours_start=s.quiet_hours_start,
            quiet_hours_end=s.quiet_hours_end,
            timezone=s.timezone,
            notification_privacy_mode=s.notification_privacy_mode,
            retention_days=s.retention_days,
            updated_at=s.updated_at,
        )


windows_lifecycle = WindowsLifecycleManager()
