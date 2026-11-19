"""Master Monitoring Run Coordinator orchestrating Stage 26 discovery through Stage 30 alerts."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any, Optional
from uuid import uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db_session
from app.db.models import (
    JobListing,
    JobSource,
    RecruitmentJobChangeEventModel,
    RecruitmentJobWatchModel,
    RecruitmentMonitoringRunModel,
)
from app.recruitment.discovery.contracts import SnapshotCompleteness
from app.recruitment.discovery.service import job_discovery_service
from app.recruitment.intelligence.service import job_intelligence_service
from app.recruitment.matching.service import job_matching_service
from app.recruitment.monitoring.alerts.engine import alert_engine
from app.recruitment.monitoring.alerts.outbox import notification_outbox
from app.recruitment.monitoring.changes.detection import detect_job_changes
from app.recruitment.monitoring.contracts import (
    AlertSeverity,
    AlertTriggerType,
    JobChangeType,
    MonitoringRunData,
    PipelinePhase,
    RunStatus,
    RunTriggerType,
    ScheduleConfig,
    WatchStatus,
)
from app.recruitment.monitoring.errors import (
    EmergencyStopActiveError,
    LeaseConflictError,
    QuotaExceededError,
    RunNotFoundError,
    WatchNotFoundError,
)
from app.recruitment.monitoring.execution.budgets import budget_controller
from app.recruitment.monitoring.execution.leases import lease_manager
from app.recruitment.monitoring.observability.health import health_monitor
from app.recruitment.monitoring.opportunities.queue import opportunity_queue_manager
from app.recruitment.monitoring.pipeline.checkpoints import CheckpointState
from app.recruitment.monitoring.pipeline.dependency_graph import dependency_graph
from app.recruitment.monitoring.scheduling.recurrence import calculate_next_occurrence
from app.security.authorization.emergency import EmergencyStopController

logger = logging.getLogger("autonom.recruitment.monitoring.execution.coordinator")


class MonitoringRunCoordinator:
    """Orchestrates end-to-end continuous job discovery, change detection, matching refresh, and queue updates."""

    async def execute_run(
        self,
        watch_id: str,
        trigger_type: RunTriggerType = RunTriggerType.SCHEDULED,
        worker_id: str = "worker-01",
        applicant_profile_id: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
    ) -> MonitoringRunData:
        """Executes a single end-to-end monitoring run for a watch."""
        if db_session:
            return await self._execute_run_internal(
                watch_id=watch_id,
                trigger_type=trigger_type,
                worker_id=worker_id,
                applicant_profile_id=applicant_profile_id,
                session=db_session,
            )
        else:
            async with get_db_session() as session:
                return await self._execute_run_internal(
                    watch_id=watch_id,
                    trigger_type=trigger_type,
                    worker_id=worker_id,
                    applicant_profile_id=applicant_profile_id,
                    session=session,
                )

    async def _execute_run_internal(
        self,
        watch_id: str,
        trigger_type: RunTriggerType,
        worker_id: str,
        applicant_profile_id: Optional[str],
        session: AsyncSession,
    ) -> MonitoringRunData:
        # 1. Emergency Stop Check
        em_ctrl = EmergencyStopController.get_instance()
        if em_ctrl.is_emergency_stop_active or em_ctrl.is_automation_paused:
            raise EmergencyStopActiveError("Monitoring run blocked: Emergency Stop or Automation Pause is active.")

        # 2. Load Watch
        stmt_w = select(RecruitmentJobWatchModel).where(RecruitmentJobWatchModel.id == watch_id)
        res_w = await session.execute(stmt_w)
        watch = res_w.scalar_one_or_none()
        if not watch:
            raise WatchNotFoundError(f"Job watch '{watch_id}' not found.")

        if watch.status == WatchStatus.PAUSED.value:
            raise EmergencyStopActiveError(f"Job watch '{watch_id}' is currently paused.")

        # 3. Worker Lease Acquisition
        lease_key = f"watch:{watch_id}"
        acquired = await lease_manager.acquire_lease(lease_key, worker_id, session)
        if not acquired:
            raise LeaseConflictError(f"Task lease for watch '{watch_id}' is held by another active worker.")

        sources_to_check = list(watch.approved_sources_json or [])
        if not sources_to_check:
            # If no specific source IDs listed, check employer boards or all enabled sources
            sources_to_check = [s.id for s in job_discovery_service.list_sources(enabled_only=True)]

        # 4. Resource Budget Reservation
        try:
            await budget_controller.check_and_reserve_run(source_count=len(sources_to_check))
        except QuotaExceededError as exc:
            await lease_manager.release_lease(lease_key, worker_id, session)
            raise exc

        # 5. Create Monitoring Run Record
        now = datetime.now(UTC)
        run = RecruitmentMonitoringRunModel(
            watch_id=watch_id,
            watch_version=watch.version,
            trigger_type=trigger_type.value,
            scheduled_at=watch.next_due_run_at,
            started_at=now,
            sources_checked_json=sources_to_check,
            career_strategy_version=1,
            authorization_context_json={"owner_id": watch.owner_id},
            resource_budget_json={"estimated_requests": len(sources_to_check) * 3},
            current_phase=PipelinePhase.DISCOVERING.value,
            status=RunStatus.RUNNING.value,
            progress_pct=10.0,
            checkpoint_state_json={},
        )
        session.add(run)
        await session.flush()

        checkpoint = CheckpointState()
        profile_id = applicant_profile_id or watch.owner_id

        try:
            # -----------------------------------------------------------------
            # Phase A: Discovery / Source Refresh
            # -----------------------------------------------------------------
            checkpoint.set_phase(PipelinePhase.DISCOVERING)
            run.current_phase = PipelinePhase.DISCOVERING.value
            run.progress_pct = 20.0

            discovered_observations = []
            for src_id in sources_to_check:
                # Check provider cooldown
                if budget_controller.is_in_cooldown(src_id):
                    logger.warning(f"Skipping source '{src_id}' due to active cooldown.")
                    continue

                try:
                    snapshot = await job_discovery_service.refresh_source(src_id)
                    run.sources_checked += 1
                    checkpoint.mark_completed_source(src_id)

                    # INVARIANT: Partial snapshots must NEVER mass-close postings!
                    if snapshot.completeness == SnapshotCompleteness.PARTIAL:
                        logger.warning(f"Source '{src_id}' snapshot is partial; preserving unobserved vacancies.")

                    # Collect newly discovered observations
                    discovered_observations.extend(snapshot.observations)
                    run.new_observations_count += len(snapshot.observations)
                except Exception as src_exc:
                    logger.error(f"Error fetching source '{src_id}': {src_exc}")
                    # Record source failure alert if severe
                    await alert_engine.evaluate_and_emit(
                        owner_id=watch.owner_id,
                        trigger_type=AlertTriggerType.SOURCE_FAILURE,
                        title=f"Source Fetch Warning: {src_id}",
                        message=f"Failed to fetch updates from source '{src_id}': {src_exc}",
                        severity=AlertSeverity.WARNING,
                        run_id=run.id,
                        session=session,
                    )

            # -----------------------------------------------------------------
            # Phase B: Canonical Aggregation & Change Detection
            # -----------------------------------------------------------------
            checkpoint.set_phase(PipelinePhase.AGGREGATING)
            run.current_phase = PipelinePhase.AGGREGATING.value
            run.progress_pct = 40.0

            # Ensure default job source exists if none
            stmt_default_source = select(JobSource).limit(1)
            res_def_src = await session.execute(stmt_default_source)
            default_source = res_def_src.scalar_one_or_none()
            if not default_source:
                default_source = JobSource(
                    platform_name="autonom_monitoring",
                    source_url="https://autonom.local/jobs",
                    source_type="web",
                    enabled=True,
                )
                session.add(default_source)
                await session.flush()

            # Process observations into canonical JobListing records
            for obs in discovered_observations:
                external_id = obs.native_posting_id or obs.observation_id
                company = obs.raw_fields.get("company") or obs.raw_fields.get("employer") or "Target Employer"
                title = obs.raw_fields.get("title") or "Software Engineer"
                app_url = obs.raw_fields.get("application_url") or obs.raw_fields.get("job_url") or f"https://example.com/jobs/{external_id}"
                desc = obs.raw_fields.get("description") or ""
                salary = obs.raw_fields.get("salary_range")
                loc = obs.raw_fields.get("location")
                work_arr = obs.raw_fields.get("work_arrangement")

                # Query existing canonical listing
                stmt_existing = select(JobListing).where(
                    JobListing.company == company,
                    JobListing.title == title,
                )
                res_existing = await session.execute(stmt_existing)
                existing_job = res_existing.scalar_one_or_none()

                new_data = {
                    "id": existing_job.id if existing_job else str(uuid4()),
                    "external_id": external_id,
                    "company": company,
                    "title": title,
                    "application_url": app_url,
                    "description": desc,
                    "salary_range": salary,
                    "location": loc,
                    "work_arrangement": work_arr,
                    "status": "active",
                }

                existing_dict = None
                if existing_job:
                    existing_dict = {
                        "id": existing_job.id,
                        "company": existing_job.company,
                        "title": existing_job.title,
                        "application_url": existing_job.application_url,
                        "description": existing_job.description,
                        "salary_range": existing_job.salary_range,
                        "location": existing_job.location,
                        "work_arrangement": existing_job.work_arrangement,
                        "status": existing_job.status,
                    }

                # Detect changes
                detected = detect_job_changes(existing_dict, new_data)

                canonical_job_record = None
                if not existing_job:
                    # Create new canonical job
                    canonical_job_record = JobListing(
                        id=new_data["id"],
                        source_id=default_source.id,
                        external_id=external_id,
                        company=company,
                        title=title,
                        application_url=app_url,
                        description=desc,
                        salary_range=salary,
                        location=loc,
                        work_arrangement=work_arr,
                        status="active",
                        discovered_at=now,
                        last_verified_at=now,
                    )
                    session.add(canonical_job_record)
                    await session.flush()
                    run.canonical_jobs_created += 1
                else:
                    canonical_job_record = existing_job
                    # Update fields if changed
                    if detected:
                        existing_job.description = desc
                        existing_job.salary_range = salary
                        existing_job.location = loc
                        existing_job.work_arrangement = work_arr
                        existing_job.application_url = app_url
                        existing_job.last_verified_at = now
                        run.canonical_jobs_updated += 1

                # Persist detected change events
                for chg in detected:
                    chg_record = RecruitmentJobChangeEventModel(
                        canonical_job_id=canonical_job_record.id,
                        source_id=obs.source_id,
                        run_id=run.id,
                        change_type=chg.change_type.value,
                        is_material=chg.is_material,
                        field_name=chg.field_name,
                        previous_value_json=chg.previous_value,
                        current_value_json=chg.current_value,
                    )
                    session.add(chg_record)

                await session.flush()

                # -------------------------------------------------------------
                # Phase C: Requirement Intelligence Reanalysis
                # -------------------------------------------------------------
                # Reanalyze if new vacancy or material description change
                has_material_change = any(c.is_material for c in detected)
                if not existing_dict or has_material_change:
                    run.current_phase = PipelinePhase.ANALYZING.value
                    run.progress_pct = 60.0
                    try:
                        await job_intelligence_service.analyze_job(
                            canonical_job_id=canonical_job_record.id,
                            force=bool(existing_dict),
                            use_ai=False,  # deterministic fast analysis
                            db_session=session,
                        )
                        run.intelligence_analyses_triggered += 1
                    except Exception as intell_exc:
                        logger.error(f"Intelligence analysis failed for {canonical_job_record.id}: {intell_exc}")

                # -------------------------------------------------------------
                # Phase D: Qualification Matching Recalculation
                # -------------------------------------------------------------
                run.current_phase = PipelinePhase.MATCHING.value
                run.progress_pct = 75.0

                evaluation = None
                try:
                    evaluation = await job_matching_service.evaluate_job(
                        canonical_job_id=canonical_job_record.id,
                        applicant_profile_id=profile_id,
                        career_strategy_id=watch.career_strategy_id,
                        force_recalculate=True,
                        db_session=session,
                    )
                    run.matches_recalculated += 1
                except Exception as match_exc:
                    logger.error(f"Job matching evaluation failed for {canonical_job_record.id}: {match_exc}")

                # -------------------------------------------------------------
                # Phase E: Opportunity Queue Update
                # -------------------------------------------------------------
                run.current_phase = PipelinePhase.UPDATING_QUEUE.value
                run.progress_pct = 85.0

                canonical_dict = {
                    "id": canonical_job_record.id,
                    "title": canonical_job_record.title,
                    "company": canonical_job_record.company,
                    "location": canonical_job_record.location,
                    "employment_type": canonical_job_record.employment_type,
                    "work_arrangement": canonical_job_record.work_arrangement,
                    "salary_range": canonical_job_record.salary_range,
                    "application_url": canonical_job_record.application_url,
                    "status": canonical_job_record.status,
                }

                queue_entry = await opportunity_queue_manager.upsert_entry(
                    canonical_job=canonical_dict,
                    applicant_profile_id=profile_id,
                    evaluation=evaluation,
                    career_strategy_id=watch.career_strategy_id,
                    session=session,
                )
                run.queue_entries_created += 1

                # -------------------------------------------------------------
                # Phase F: Alert Rules Evaluation & Notification Dispatch
                # -------------------------------------------------------------
                run.current_phase = PipelinePhase.EVALUATING_ALERTS.value
                run.progress_pct = 95.0

                if not existing_dict:
                    # New opportunity alert
                    new_alert = await alert_engine.evaluate_and_emit(
                        owner_id=watch.owner_id,
                        trigger_type=AlertTriggerType.NEW_JOB,
                        title=f"New Opportunity: {canonical_job_record.title} at {canonical_job_record.company}",
                        message=f"Discovered new vacancy '{canonical_job_record.title}' aligned with your profile.",
                        severity=AlertSeverity.INFO,
                        canonical_job_id=canonical_job_record.id,
                        queue_entry_id=queue_entry.id,
                        run_id=run.id,
                        session=session,
                    )
                    if new_alert:
                        run.alerts_generated += 1

                # High-priority alert
                if evaluation and evaluation.overall_score >= 80.0 and evaluation.hard_policy_passed:
                    hp_alert = await alert_engine.evaluate_and_emit(
                        owner_id=watch.owner_id,
                        trigger_type=AlertTriggerType.HIGH_PRIORITY_JOB,
                        title=f"High-Priority Match: {canonical_job_record.title} ({int(evaluation.overall_score)}%)",
                        message=f"Outstanding match at {canonical_job_record.company} meets target career requirements.",
                        severity=AlertSeverity.INFO,
                        canonical_job_id=canonical_job_record.id,
                        queue_entry_id=queue_entry.id,
                        run_id=run.id,
                        session=session,
                    )
                    if hp_alert:
                        run.alerts_generated += 1

                # Job change alert for material changes
                if existing_dict and has_material_change:
                    chg_alert = await alert_engine.evaluate_and_emit(
                        owner_id=watch.owner_id,
                        trigger_type=AlertTriggerType.MATERIAL_JOB_CHANGE,
                        title=f"Job Requirements Updated: {canonical_job_record.title}",
                        message=f"Material changes detected in job requirements for {canonical_job_record.company}.",
                        severity=AlertSeverity.INFO,
                        canonical_job_id=canonical_job_record.id,
                        queue_entry_id=queue_entry.id,
                        run_id=run.id,
                        session=session,
                    )
                    if chg_alert:
                        run.alerts_generated += 1

            # Dispatch notification outbox
            await notification_outbox.process_outbox(session=session)

            # Mark completed
            run.current_phase = PipelinePhase.COMPLETED.value
            run.status = RunStatus.COMPLETED.value
            run.progress_pct = 100.0
            run.ended_at = datetime.now(UTC)

            # Update Watch last run & next due
            watch.last_run_at = run.ended_at
            watch.consecutive_failures = 0
            watch.error_state = None
            sched = ScheduleConfig(**(watch.schedule_config_json or {}))
            watch.next_due_run_at = calculate_next_occurrence(sched, after_time=run.ended_at)

            await session.flush()
            return self._to_run_data(run)

        except Exception as exc:
            logger.error(f"Monitoring run failed for watch '{watch_id}': {exc}", exc_info=True)
            run.status = RunStatus.FAILED.value
            run.error_message = str(exc)
            run.ended_at = datetime.now(UTC)

            watch.consecutive_failures += 1
            watch.error_state = str(exc)
            if watch.consecutive_failures >= 3:
                watch.status = WatchStatus.FAILED.value

            await session.flush()
            raise exc

        finally:
            # Release lease and budget
            await lease_manager.release_lease(lease_key, worker_id, session)
            await budget_controller.release_run()

    async def get_run(self, run_id: str, session: AsyncSession) -> MonitoringRunData:
        stmt = select(RecruitmentMonitoringRunModel).where(RecruitmentMonitoringRunModel.id == run_id)
        res = await session.execute(stmt)
        run = res.scalar_one_or_none()
        if not run:
            raise RunNotFoundError(f"Monitoring run '{run_id}' not found.")
        return self._to_run_data(run)

    async def list_runs(
        self,
        session: AsyncSession,
        watch_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MonitoringRunData]:
        stmt = select(RecruitmentMonitoringRunModel)
        if watch_id:
            stmt = stmt.where(RecruitmentMonitoringRunModel.watch_id == watch_id)

        stmt = stmt.order_by(RecruitmentMonitoringRunModel.started_at.desc()).limit(limit).offset(offset)
        res = await session.execute(stmt)
        items = list(res.scalars().all())
        return [self._to_run_data(r) for r in items]

    async def cancel_run(self, run_id: str, session: AsyncSession) -> bool:
        stmt = select(RecruitmentMonitoringRunModel).where(RecruitmentMonitoringRunModel.id == run_id)
        res = await session.execute(stmt)
        run = res.scalar_one_or_none()
        if not run or run.status not in (RunStatus.RUNNING.value, RunStatus.QUEUED.value):
            return False

        run.status = RunStatus.CANCELLED.value
        run.ended_at = datetime.now(UTC)
        await session.flush()
        return True

    def _to_run_data(self, r: RecruitmentMonitoringRunModel) -> MonitoringRunData:
        return MonitoringRunData(
            id=r.id,
            watch_id=r.watch_id,
            watch_version=r.watch_version,
            trigger_type=RunTriggerType(r.trigger_type),
            scheduled_at=r.scheduled_at,
            started_at=r.started_at,
            ended_at=r.ended_at,
            sources_checked_list=r.sources_checked_json or [],
            current_phase=PipelinePhase(r.current_phase),
            status=RunStatus(r.status),
            progress_pct=r.progress_pct,
            sources_checked=r.sources_checked,
            new_observations_count=r.new_observations_count,
            updated_observations_count=r.updated_observations_count,
            canonical_jobs_created=r.canonical_jobs_created,
            canonical_jobs_updated=r.canonical_jobs_updated,
            intelligence_analyses_triggered=r.intelligence_analyses_triggered,
            matches_recalculated=r.matches_recalculated,
            queue_entries_created=r.queue_entries_created,
            alerts_generated=r.alerts_generated,
            error_message=r.error_message,
            output_references=r.output_references_json or {},
        )


monitoring_run_coordinator = MonitoringRunCoordinator()
