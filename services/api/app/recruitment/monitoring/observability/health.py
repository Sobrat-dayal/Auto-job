"""Component and Agent Operational Health Monitor."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RecruitmentMonitoringHealthModel
from app.recruitment.monitoring.contracts import (
    ComponentHealthData,
    ComponentHealthStatus,
)


class HealthMonitor:
    """Tracks component heartbeats and operational statuses."""

    DEFAULT_COMPONENTS = [
        "scheduler",
        "worker_manager",
        "source_monitor",
        "alert_dispatcher",
        "queue_manager",
        "windows_lifecycle",
        "supervisor_agent",
        "discovery_agent",
        "intelligence_agent",
        "matching_agent",
    ]

    async def record_heartbeat(
        self,
        component: str,
        status: ComponentHealthStatus,
        details: dict[str, Any],
        session: AsyncSession,
    ) -> None:
        stmt = select(RecruitmentMonitoringHealthModel).where(
            RecruitmentMonitoringHealthModel.component == component
        )
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()

        now = datetime.now(UTC)
        if record:
            record.status = status.value
            record.heartbeat_at = now
            record.details_json = details
        else:
            record = RecruitmentMonitoringHealthModel(
                component=component,
                status=status.value,
                heartbeat_at=now,
                details_json=details,
            )
            session.add(record)

        await session.flush()

    async def list_health(self, session: AsyncSession) -> list[ComponentHealthData]:
        stmt = select(RecruitmentMonitoringHealthModel)
        res = await session.execute(stmt)
        records = {r.component: r for r in res.scalars().all()}

        results = []
        now = datetime.now(UTC)
        for comp in self.DEFAULT_COMPONENTS:
            if comp in records:
                r = records[comp]
                results.append(
                    ComponentHealthData(
                        component=r.component,
                        status=ComponentHealthStatus(r.status),
                        heartbeat_at=r.heartbeat_at,
                        details=r.details_json or {},
                    )
                )
            else:
                results.append(
                    ComponentHealthData(
                        component=comp,
                        status=ComponentHealthStatus.AVAILABLE,
                        heartbeat_at=now,
                        details={"status": "initialized"},
                    )
                )

        return results


health_monitor = HealthMonitor()
