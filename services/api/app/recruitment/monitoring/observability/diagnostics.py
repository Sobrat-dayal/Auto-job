"""System Diagnostics and Health Aggregator for Stage 30 Recruitment Monitoring."""

from __future__ import annotations

from datetime import UTC, datetime
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    RecruitmentNotificationOutboxModel,
    RecruitmentWorkerLeaseModel,
)
from app.recruitment.monitoring.contracts import DiagnosticsReport
from app.recruitment.monitoring.execution.budgets import budget_controller
from app.recruitment.monitoring.observability.health import health_monitor
from app.recruitment.monitoring.scheduling.quiet_hours import is_in_quiet_hours
from app.security.authorization.emergency import EmergencyStopController


class DiagnosticsAggregator:
    """Produces unified system diagnostics and error reports."""

    async def get_diagnostics(
        self,
        timezone: str,
        session: AsyncSession,
    ) -> DiagnosticsReport:
        now = datetime.now(UTC)

        # Emergency stop
        em_ctrl = EmergencyStopController.get_instance()
        em_active = em_ctrl.is_emergency_stop_active
        auto_paused = em_ctrl.is_automation_paused

        # Active worker leases
        stmt_leases = select(func.count(RecruitmentWorkerLeaseModel.id)).where(
            RecruitmentWorkerLeaseModel.expires_at > now
        )
        active_leases = (await session.execute(stmt_leases)).scalar() or 0

        # Pending outbox items
        stmt_outbox = select(func.count(RecruitmentNotificationOutboxModel.id)).where(
            RecruitmentNotificationOutboxModel.status == "pending"
        )
        pending_outbox = (await session.execute(stmt_outbox)).scalar() or 0

        # Component health
        health_list = await health_monitor.list_health(session)

        # Active cooldowns
        cooldowns = budget_controller.get_all_cooldowns()

        from app.recruitment.monitoring.contracts import QuietHoursConfig
        qh_active = is_in_quiet_hours(QuietHoursConfig(), now, timezone)

        return DiagnosticsReport(
            system_time_utc=now,
            timezone_configured=timezone,
            is_quiet_hours_now=qh_active,
            database_status="healthy",
            emergency_stop_active=em_active,
            automation_paused=auto_paused,
            active_worker_leases=active_leases,
            pending_outbox_notifications=pending_outbox,
            components_health=health_list,
            active_cooldowns=cooldowns,
        )


diagnostics_aggregator = DiagnosticsAggregator()
