"""Singleton Recruitment Monitoring Service for Stage 30."""

from __future__ import annotations

import logging
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db_session
from app.db.models import RecruitmentJobChangeEventModel
from app.recruitment.discovery.contracts import JobSourceHealth
from app.recruitment.discovery.service import job_discovery_service
from app.recruitment.monitoring.alerts.engine import alert_engine
from app.recruitment.monitoring.alerts.outbox import notification_outbox
from app.recruitment.monitoring.contracts import (
    AlertEventData,
    AlertRuleCreateRequest,
    AlertRuleData,
    AlertRuleUpdateRequest,
    ComponentHealthData,
    DiagnosticsReport,
    JobChangeEventData,
    JobChangeType,
    JobWatchCreateRequest,
    JobWatchData,
    JobWatchUpdateRequest,
    MonitoringMetricsData,
    MonitoringOverviewKPIs,
    MonitoringProfileCreateRequest,
    MonitoringProfileData,
    MonitoringProfileUpdateRequest,
    MonitoringRunData,
    MonitoringSettingsData,
    MonitoringSettingsUpdateRequest,
    NotificationOutboxData,
    OpportunityQueueEntryData,
    OpportunityQueueUpdateRequest,
    RunTriggerType,
    SchedulePreviewResponse,
    WatchStatus,
)
from app.recruitment.monitoring.execution.coordinator import monitoring_run_coordinator
from app.recruitment.monitoring.observability.diagnostics import diagnostics_aggregator
from app.recruitment.monitoring.observability.health import health_monitor
from app.recruitment.monitoring.observability.metrics import metrics_collector
from app.recruitment.monitoring.opportunities.queue import opportunity_queue_manager
from app.recruitment.monitoring.platform.windows_lifecycle import windows_lifecycle
from app.recruitment.monitoring.scheduling.preview import generate_schedule_preview
from app.recruitment.monitoring.watches.registry import watch_registry
from app.recruitment.monitoring.watches.validation import validate_watch_request

logger = logging.getLogger("autonom.recruitment.monitoring.service")


class RecruitmentMonitoringService:
    """High-level facade for continuous job discovery, autonomous source monitoring, and opportunity queue."""

    # -------------------------------------------------------------------------
    # Profiles
    # -------------------------------------------------------------------------

    async def create_profile(
        self,
        owner_id: str,
        req: MonitoringProfileCreateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringProfileData:
        if db_session:
            return await watch_registry.create_profile(owner_id, req, db_session)
        async with get_db_session() as session:
            return await watch_registry.create_profile(owner_id, req, session)

    async def get_profile(
        self,
        profile_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringProfileData:
        if db_session:
            return await watch_registry.get_profile(profile_id, db_session)
        async with get_db_session() as session:
            return await watch_registry.get_profile(profile_id, session)

    async def list_profiles(
        self,
        owner_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> list[MonitoringProfileData]:
        if db_session:
            return await watch_registry.list_profiles(owner_id, db_session)
        async with get_db_session() as session:
            return await watch_registry.list_profiles(owner_id, session)

    async def update_profile(
        self,
        profile_id: str,
        req: MonitoringProfileUpdateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringProfileData:
        if db_session:
            return await watch_registry.update_profile(profile_id, req, db_session)
        async with get_db_session() as session:
            return await watch_registry.update_profile(profile_id, req, session)

    # -------------------------------------------------------------------------
    # Watches
    # -------------------------------------------------------------------------

    async def create_watch(
        self,
        owner_id: str,
        req: JobWatchCreateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> JobWatchData:
        if db_session:
            return await watch_registry.create_watch(owner_id, req, db_session)
        async with get_db_session() as session:
            return await watch_registry.create_watch(owner_id, req, session)

    async def get_watch(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> JobWatchData:
        if db_session:
            return await watch_registry.get_watch(watch_id, db_session)
        async with get_db_session() as session:
            return await watch_registry.get_watch(watch_id, session)

    async def list_watches(
        self,
        owner_id: str,
        profile_id: Optional[str] = None,
        status: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> list[JobWatchData]:
        if db_session:
            return await watch_registry.list_watches(owner_id, db_session, profile_id, status)
        async with get_db_session() as session:
            return await watch_registry.list_watches(owner_id, session, profile_id, status)

    async def update_watch(
        self,
        watch_id: str,
        req: JobWatchUpdateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> JobWatchData:
        if db_session:
            return await watch_registry.update_watch(watch_id, req, db_session)
        async with get_db_session() as session:
            return await watch_registry.update_watch(watch_id, req, session)

    async def delete_watch(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        if db_session:
            return await watch_registry.delete_watch(watch_id, db_session)
        async with get_db_session() as session:
            return await watch_registry.delete_watch(watch_id, session)

    async def validate_watch(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> dict[str, Any]:
        watch = await self.get_watch(watch_id, db_session)
        # Re-run validation rules
        from app.recruitment.monitoring.contracts import JobWatchCreateRequest
        dummy_req = JobWatchCreateRequest(
            profile_id=watch.profile_id,
            name=watch.name,
            watch_type=watch.watch_type,
            career_strategy_id=watch.career_strategy_id,
            approved_sources=watch.approved_sources,
            employer_ids=watch.employer_ids,
            role_filters=watch.role_filters,
            location_filters=watch.location_filters,
            schedule_config=watch.schedule_config,
            alert_rules=watch.alert_rules,
        )
        validate_watch_request(dummy_req)
        return {"valid": True, "watch_id": watch_id, "status": watch.status.value}

    async def activate_watch(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> JobWatchData:
        if db_session:
            return await watch_registry.set_watch_status(watch_id, WatchStatus.ACTIVE, db_session)
        async with get_db_session() as session:
            return await watch_registry.set_watch_status(watch_id, WatchStatus.ACTIVE, session)

    async def pause_watch(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> JobWatchData:
        if db_session:
            return await watch_registry.set_watch_status(watch_id, WatchStatus.PAUSED, db_session)
        async with get_db_session() as session:
            return await watch_registry.set_watch_status(watch_id, WatchStatus.PAUSED, session)

    async def resume_watch(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> JobWatchData:
        if db_session:
            return await watch_registry.set_watch_status(watch_id, WatchStatus.ACTIVE, db_session)
        async with get_db_session() as session:
            return await watch_registry.set_watch_status(watch_id, WatchStatus.ACTIVE, session)

    async def preview_schedule(
        self,
        watch_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> SchedulePreviewResponse:
        watch = await self.get_watch(watch_id, db_session)
        return generate_schedule_preview(
            watch_name=watch.name,
            schedule=watch.schedule_config,
            source_count=len(watch.approved_sources) or 1,
            requires_authorization=False,
        )

    # -------------------------------------------------------------------------
    # Execution & Runs
    # -------------------------------------------------------------------------

    async def run_now(
        self,
        watch_id: str,
        worker_id: str = "worker-manual",
        applicant_profile_id: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringRunData:
        return await monitoring_run_coordinator.execute_run(
            watch_id=watch_id,
            trigger_type=RunTriggerType.MANUAL,
            worker_id=worker_id,
            applicant_profile_id=applicant_profile_id,
            db_session=db_session,
        )

    async def get_run(
        self,
        run_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringRunData:
        if db_session:
            return await monitoring_run_coordinator.get_run(run_id, db_session)
        async with get_db_session() as session:
            return await monitoring_run_coordinator.get_run(run_id, session)

    async def list_runs(
        self,
        watch_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db_session: Optional[AsyncSession] = None,
    ) -> list[MonitoringRunData]:
        if db_session:
            return await monitoring_run_coordinator.list_runs(db_session, watch_id, limit, offset)
        async with get_db_session() as session:
            return await monitoring_run_coordinator.list_runs(session, watch_id, limit, offset)

    async def cancel_run(
        self,
        run_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        if db_session:
            return await monitoring_run_coordinator.cancel_run(run_id, db_session)
        async with get_db_session() as session:
            return await monitoring_run_coordinator.cancel_run(run_id, session)

    # -------------------------------------------------------------------------
    # Opportunity Queue
    # -------------------------------------------------------------------------

    async def get_opportunity(
        self,
        entry_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> OpportunityQueueEntryData:
        if db_session:
            return await opportunity_queue_manager.get_entry(entry_id, db_session)
        async with get_db_session() as session:
            return await opportunity_queue_manager.get_entry(entry_id, session)

    async def list_opportunities(
        self,
        applicant_profile_id: str,
        priority: Optional[str] = None,
        queue_status: Optional[str] = None,
        ready_for_preparation: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
        db_session: Optional[AsyncSession] = None,
    ) -> list[OpportunityQueueEntryData]:
        if db_session:
            return await opportunity_queue_manager.list_entries(
                applicant_profile_id, db_session, priority, queue_status, ready_for_preparation, limit, offset
            )
        async with get_db_session() as session:
            return await opportunity_queue_manager.list_entries(
                applicant_profile_id, session, priority, queue_status, ready_for_preparation, limit, offset
            )

    async def update_opportunity(
        self,
        entry_id: str,
        req: OpportunityQueueUpdateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> OpportunityQueueEntryData:
        if db_session:
            return await opportunity_queue_manager.update_entry(entry_id, req, db_session)
        async with get_db_session() as session:
            return await opportunity_queue_manager.update_entry(entry_id, req, session)

    # -------------------------------------------------------------------------
    # Job Changes
    # -------------------------------------------------------------------------

    async def list_job_changes(
        self,
        canonical_job_id: Optional[str] = None,
        limit: int = 50,
        db_session: Optional[AsyncSession] = None,
    ) -> list[JobChangeEventData]:
        async def _query(session: AsyncSession):
            stmt = select(RecruitmentJobChangeEventModel)
            if canonical_job_id:
                stmt = stmt.where(RecruitmentJobChangeEventModel.canonical_job_id == canonical_job_id)
            stmt = stmt.order_by(RecruitmentJobChangeEventModel.detected_at.desc()).limit(limit)
            res = await session.execute(stmt)
            items = list(res.scalars().all())
            return [
                JobChangeEventData(
                    id=c.id,
                    canonical_job_id=c.canonical_job_id,
                    source_id=c.source_id,
                    run_id=c.run_id,
                    change_type=JobChangeType(c.change_type),
                    is_material=c.is_material,
                    field_name=c.field_name,
                    previous_value=c.previous_value_json,
                    current_value=c.current_value_json,
                    detected_at=c.detected_at,
                )
                for c in items
            ]

        if db_session:
            return await _query(db_session)
        async with get_db_session() as session:
            return await _query(session)

    # -------------------------------------------------------------------------
    # Alerts & Notifications
    # -------------------------------------------------------------------------

    async def create_alert_rule(
        self,
        owner_id: str,
        req: AlertRuleCreateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> AlertRuleData:
        if db_session:
            return await alert_engine.create_rule(owner_id, req, db_session)
        async with get_db_session() as session:
            return await alert_engine.create_rule(owner_id, req, session)

    async def update_alert_rule(
        self,
        rule_id: str,
        req: AlertRuleUpdateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> AlertRuleData:
        if db_session:
            return await alert_engine.update_rule(rule_id, req, db_session)
        async with get_db_session() as session:
            return await alert_engine.update_rule(rule_id, req, session)

    async def list_alert_rules(
        self,
        owner_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> list[AlertRuleData]:
        if db_session:
            return await alert_engine.list_rules(owner_id, db_session)
        async with get_db_session() as session:
            return await alert_engine.list_rules(owner_id, session)

    async def list_alerts(
        self,
        owner_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        db_session: Optional[AsyncSession] = None,
    ) -> list[AlertEventData]:
        if db_session:
            return await alert_engine.list_alerts(owner_id, db_session, unread_only, limit, offset)
        async with get_db_session() as session:
            return await alert_engine.list_alerts(owner_id, session, unread_only, limit, offset)

    async def acknowledge_alert(
        self,
        alert_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        if db_session:
            return await alert_engine.acknowledge_alert(alert_id, db_session)
        async with get_db_session() as session:
            return await alert_engine.acknowledge_alert(alert_id, session)

    async def dismiss_alert(
        self,
        alert_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        if db_session:
            return await alert_engine.dismiss_alert(alert_id, db_session)
        async with get_db_session() as session:
            return await alert_engine.dismiss_alert(alert_id, session)

    async def list_notifications(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        db_session: Optional[AsyncSession] = None,
    ) -> list[NotificationOutboxData]:
        if db_session:
            return await notification_outbox.list_notifications(db_session, status, limit)
        async with get_db_session() as session:
            return await notification_outbox.list_notifications(session, status, limit)

    async def mark_notification_read(
        self,
        notification_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> bool:
        if db_session:
            return await notification_outbox.mark_as_read(notification_id, db_session)
        async with get_db_session() as session:
            return await notification_outbox.mark_as_read(notification_id, session)

    # -------------------------------------------------------------------------
    # Health, Metrics & Settings
    # -------------------------------------------------------------------------

    def list_source_health(self) -> list[JobSourceHealth]:
        return job_discovery_service.list_all_health()

    async def list_worker_health(
        self,
        db_session: Optional[AsyncSession] = None,
    ) -> list[ComponentHealthData]:
        if db_session:
            return await health_monitor.list_health(db_session)
        async with get_db_session() as session:
            return await health_monitor.list_health(session)

    async def get_overview_kpis(
        self,
        owner_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringOverviewKPIs:
        if db_session:
            return await metrics_collector.get_overview_kpis(owner_id, db_session)
        async with get_db_session() as session:
            return await metrics_collector.get_overview_kpis(owner_id, session)

    async def get_metrics(
        self,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringMetricsData:
        if db_session:
            return await metrics_collector.get_metrics(db_session)
        async with get_db_session() as session:
            return await metrics_collector.get_metrics(session)

    async def get_diagnostics(
        self,
        timezone: str = "UTC",
        db_session: Optional[AsyncSession] = None,
    ) -> DiagnosticsReport:
        if db_session:
            return await diagnostics_aggregator.get_diagnostics(timezone, db_session)
        async with get_db_session() as session:
            return await diagnostics_aggregator.get_diagnostics(timezone, session)

    async def get_settings(
        self,
        owner_id: str,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringSettingsData:
        if db_session:
            return await windows_lifecycle.get_settings(owner_id, db_session)
        async with get_db_session() as session:
            return await windows_lifecycle.get_settings(owner_id, session)

    async def update_settings(
        self,
        owner_id: str,
        req: MonitoringSettingsUpdateRequest,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringSettingsData:
        if db_session:
            return await windows_lifecycle.update_settings(owner_id, req, db_session)
        async with get_db_session() as session:
            return await windows_lifecycle.update_settings(owner_id, req, session)


recruitment_monitoring_service = RecruitmentMonitoringService()
