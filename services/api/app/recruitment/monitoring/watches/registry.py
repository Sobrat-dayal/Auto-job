"""Watch and Monitoring Profile Registry managing persistence and lifecycle states."""

from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    RecruitmentJobWatchModel,
    RecruitmentMonitoringProfileModel,
)
from app.recruitment.monitoring.contracts import (
    JobWatchCreateRequest,
    JobWatchData,
    JobWatchUpdateRequest,
    MonitoringProfileCreateRequest,
    MonitoringProfileData,
    MonitoringProfileUpdateRequest,
    ScheduleConfig,
    WatchStatus,
    WatchType,
)
from app.recruitment.monitoring.errors import (
    ProfileNotFoundError,
    WatchNotFoundError,
)
from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
from app.recruitment.monitoring.watches.validation import (
    validate_profile_request,
    validate_watch_request,
)

logger = logging.getLogger("autonom.recruitment.monitoring.watches.registry")


class WatchRegistry:
    """Manages CRUD and lifecycle operations for Monitoring Profiles and Job Watches."""

    # -------------------------------------------------------------------------
    # Monitoring Profiles
    # -------------------------------------------------------------------------

    async def create_profile(
        self,
        owner_id: str,
        req: MonitoringProfileCreateRequest,
        session: AsyncSession,
    ) -> MonitoringProfileData:
        validate_profile_request(req)

        profile = RecruitmentMonitoringProfileModel(
            owner_id=owner_id,
            career_strategy_id=req.career_strategy_id,
            name=req.name,
            enabled=True,
            source_scope_json=req.source_scope,
            role_scope_json=req.role_scope,
            location_scope_json=req.location_scope,
            alert_preferences_json=req.alert_preferences,
            resource_limits_json=req.resource_limits,
            review_rules_json=req.review_rules,
            retention_days=req.retention_days,
            version=1,
        )
        session.add(profile)
        await session.flush()
        return self._to_profile_data(profile)

    async def get_profile(self, profile_id: str, session: AsyncSession) -> MonitoringProfileData:
        stmt = select(RecruitmentMonitoringProfileModel).where(RecruitmentMonitoringProfileModel.id == profile_id)
        res = await session.execute(stmt)
        p = res.scalar_one_or_none()
        if not p:
            raise ProfileNotFoundError(f"Monitoring profile '{profile_id}' not found.")
        return self._to_profile_data(p)

    async def list_profiles(
        self,
        owner_id: str,
        session: AsyncSession,
    ) -> list[MonitoringProfileData]:
        stmt = select(RecruitmentMonitoringProfileModel).where(RecruitmentMonitoringProfileModel.owner_id == owner_id)
        res = await session.execute(stmt)
        items = list(res.scalars().all())
        return [self._to_profile_data(p) for p in items]

    async def update_profile(
        self,
        profile_id: str,
        req: MonitoringProfileUpdateRequest,
        session: AsyncSession,
    ) -> MonitoringProfileData:
        stmt = select(RecruitmentMonitoringProfileModel).where(RecruitmentMonitoringProfileModel.id == profile_id)
        res = await session.execute(stmt)
        p = res.scalar_one_or_none()
        if not p:
            raise ProfileNotFoundError(f"Monitoring profile '{profile_id}' not found.")

        if req.name is not None:
            p.name = req.name
        if req.career_strategy_id is not None:
            p.career_strategy_id = req.career_strategy_id
        if req.enabled is not None:
            p.enabled = req.enabled
        if req.source_scope is not None:
            p.source_scope_json = req.source_scope
        if req.role_scope is not None:
            p.role_scope_json = req.role_scope
        if req.location_scope is not None:
            p.location_scope_json = req.location_scope
        if req.alert_preferences is not None:
            p.alert_preferences_json = req.alert_preferences
        if req.resource_limits is not None:
            p.resource_limits_json = req.resource_limits
        if req.review_rules is not None:
            p.review_rules_json = req.review_rules
        if req.retention_days is not None:
            p.retention_days = req.retention_days

        p.version += 1
        p.updated_at = datetime.now(UTC)
        await session.flush()
        return self._to_profile_data(p)

    def _to_profile_data(self, p: RecruitmentMonitoringProfileModel) -> MonitoringProfileData:
        return MonitoringProfileData(
            id=p.id,
            owner_id=p.owner_id,
            career_strategy_id=p.career_strategy_id,
            career_strategy_version=p.career_strategy_version,
            name=p.name,
            enabled=p.enabled,
            source_scope=p.source_scope_json or [],
            role_scope=p.role_scope_json or [],
            location_scope=p.location_scope_json or [],
            alert_preferences=p.alert_preferences_json or {},
            resource_limits=p.resource_limits_json or {},
            review_rules=p.review_rules_json or {},
            retention_days=p.retention_days,
            version=p.version,
            active_watches_count=len(p.watches) if "watches" in p.__dict__ and p.watches else 0,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    # -------------------------------------------------------------------------
    # Job Watches
    # -------------------------------------------------------------------------

    async def create_watch(
        self,
        owner_id: str,
        req: JobWatchCreateRequest,
        session: AsyncSession,
    ) -> JobWatchData:
        validate_watch_request(req)

        # Calculate initial next due run
        next_due = calculate_next_occurrence(req.schedule_config)

        watch = RecruitmentJobWatchModel(
            owner_id=owner_id,
            profile_id=req.profile_id,
            name=req.name,
            watch_type=req.watch_type.value,
            career_strategy_id=req.career_strategy_id,
            approved_sources_json=req.approved_sources,
            employer_ids_json=req.employer_ids,
            role_filters_json=req.role_filters,
            location_filters_json=req.location_filters,
            schedule_config_json=req.schedule_config.model_dump(mode="json"),
            alert_rules_json=req.alert_rules,
            status=WatchStatus.ACTIVE.value,
            next_due_run_at=next_due,
            version=1,
        )
        session.add(watch)
        await session.flush()
        return self._to_watch_data(watch)

    async def get_watch(self, watch_id: str, session: AsyncSession) -> JobWatchData:
        stmt = select(RecruitmentJobWatchModel).where(RecruitmentJobWatchModel.id == watch_id)
        res = await session.execute(stmt)
        w = res.scalar_one_or_none()
        if not w:
            raise WatchNotFoundError(f"Job watch '{watch_id}' not found.")
        return self._to_watch_data(w)

    async def list_watches(
        self,
        owner_id: str,
        session: AsyncSession,
        profile_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[JobWatchData]:
        stmt = select(RecruitmentJobWatchModel).where(RecruitmentJobWatchModel.owner_id == owner_id)
        if profile_id:
            stmt = stmt.where(RecruitmentJobWatchModel.profile_id == profile_id)
        if status:
            stmt = stmt.where(RecruitmentJobWatchModel.status == status)

        stmt = stmt.order_by(RecruitmentJobWatchModel.created_at.desc())
        res = await session.execute(stmt)
        items = list(res.scalars().all())
        return [self._to_watch_data(w) for w in items]

    async def update_watch(
        self,
        watch_id: str,
        req: JobWatchUpdateRequest,
        session: AsyncSession,
    ) -> JobWatchData:
        stmt = select(RecruitmentJobWatchModel).where(RecruitmentJobWatchModel.id == watch_id)
        res = await session.execute(stmt)
        w = res.scalar_one_or_none()
        if not w:
            raise WatchNotFoundError(f"Job watch '{watch_id}' not found.")

        if req.name is not None:
            w.name = req.name
        if req.approved_sources is not None:
            w.approved_sources_json = req.approved_sources
        if req.employer_ids is not None:
            w.employer_ids_json = req.employer_ids
        if req.role_filters is not None:
            w.role_filters_json = req.role_filters
        if req.location_filters is not None:
            w.location_filters_json = req.location_filters
        if req.schedule_config is not None:
            w.schedule_config_json = req.schedule_config.model_dump(mode="json")
            w.next_due_run_at = calculate_next_occurrence(req.schedule_config)
        if req.alert_rules is not None:
            w.alert_rules_json = req.alert_rules
        if req.status is not None:
            w.status = req.status.value

        w.version += 1
        w.updated_at = datetime.now(UTC)
        await session.flush()
        return self._to_watch_data(w)

    async def delete_watch(self, watch_id: str, session: AsyncSession) -> bool:
        stmt = select(RecruitmentJobWatchModel).where(RecruitmentJobWatchModel.id == watch_id)
        res = await session.execute(stmt)
        w = res.scalar_one_or_none()
        if not w:
            return False
        await session.delete(w)
        await session.flush()
        return True

    async def set_watch_status(
        self,
        watch_id: str,
        new_status: WatchStatus,
        session: AsyncSession,
        error_message: Optional[str] = None,
    ) -> JobWatchData:
        stmt = select(RecruitmentJobWatchModel).where(RecruitmentJobWatchModel.id == watch_id)
        res = await session.execute(stmt)
        w = res.scalar_one_or_none()
        if not w:
            raise WatchNotFoundError(f"Job watch '{watch_id}' not found.")

        w.status = new_status.value
        if error_message is not None:
            w.error_state = error_message
        if new_status == WatchStatus.ACTIVE and not w.next_due_run_at:
            sched = ScheduleConfig(**(w.schedule_config_json or {}))
            w.next_due_run_at = calculate_next_occurrence(sched)

        w.updated_at = datetime.now(UTC)
        await session.flush()
        return self._to_watch_data(w)

    def _to_watch_data(self, w: RecruitmentJobWatchModel) -> JobWatchData:
        sched = ScheduleConfig(**(w.schedule_config_json or {}))
        return JobWatchData(
            id=w.id,
            owner_id=w.owner_id,
            profile_id=w.profile_id,
            name=w.name,
            watch_type=WatchType(w.watch_type),
            career_strategy_id=w.career_strategy_id,
            approved_sources=w.approved_sources_json or [],
            employer_ids=w.employer_ids_json or [],
            role_filters=w.role_filters_json or {},
            location_filters=w.location_filters_json or {},
            schedule_config=sched,
            alert_rules=w.alert_rules_json or {},
            status=WatchStatus(w.status),
            error_state=w.error_state,
            last_run_at=w.last_run_at,
            next_due_run_at=w.next_due_run_at,
            consecutive_failures=w.consecutive_failures,
            version=w.version,
            created_at=w.created_at,
            updated_at=w.updated_at,
        )


watch_registry = WatchRegistry()
