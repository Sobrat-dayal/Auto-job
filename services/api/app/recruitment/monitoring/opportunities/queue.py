"""Opportunity Queue Registry managing prioritized vacancies, readiness, and user actions."""

from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import Any, Optional
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    JobListing,
    JobMatchEvaluationModel,
    RecruitmentOpportunityQueueHistoryModel,
    RecruitmentOpportunityQueueModel,
)
from app.recruitment.matching.contracts import JobMatchEvaluation, MatchingOutcome
from app.recruitment.monitoring.contracts import (
    OpportunityPreparationCandidate,
    OpportunityPriority,
    OpportunityQueueEntryData,
    OpportunityQueueStatus,
    OpportunityQueueUpdateRequest,
)
from app.recruitment.monitoring.errors import QueueEntryNotFoundError
from app.recruitment.monitoring.opportunities.readiness import evaluate_preparation_readiness

logger = logging.getLogger("autonom.recruitment.monitoring.opportunities.queue")


class OpportunityQueueManager:
    """Manages persistent opportunity queue entries, priorities, review flags, and user actions."""

    async def upsert_entry(
        self,
        canonical_job: dict[str, Any],
        applicant_profile_id: str,
        evaluation: Optional[JobMatchEvaluation],
        career_strategy_id: Optional[str],
        session: AsyncSession,
    ) -> OpportunityQueueEntryData:
        """Atomically inserts or updates an opportunity queue entry."""
        job_id = canonical_job["id"]

        # Check existing entry
        stmt = select(RecruitmentOpportunityQueueModel).where(
            RecruitmentOpportunityQueueModel.canonical_job_id == job_id,
            RecruitmentOpportunityQueueModel.applicant_profile_id == applicant_profile_id,
            RecruitmentOpportunityQueueModel.career_strategy_id == career_strategy_id,
        )
        res = await session.execute(stmt)
        entry = res.scalar_one_or_none()

        # Determine priority and queue status
        priority = self._calculate_priority(evaluation)
        queue_status = self._calculate_queue_status(evaluation, canonical_job)
        readiness, candidate = evaluate_preparation_readiness(canonical_job, evaluation, priority)

        # Verify if match evaluation exists in database to avoid foreign key violations
        eval_id = None
        if evaluation and getattr(evaluation, "id", None):
            stmt_ev = select(JobMatchEvaluationModel.id).where(JobMatchEvaluationModel.id == evaluation.id)
            res_ev = await session.execute(stmt_ev)
            if res_ev.scalar_one_or_none():
                eval_id = evaluation.id

        # Review items
        raw_reviews = getattr(evaluation, "review_requests", None) or getattr(evaluation, "review_items", None) or []
        reviews = []
        for r in raw_reviews:
            if hasattr(r, "model_dump"):
                reviews.append(r.model_dump(mode="json"))
            elif isinstance(r, dict):
                reviews.append(r)
            else:
                reviews.append({"detail": str(r)})

        relevance = getattr(evaluation, "relevance_index", None)
        if relevance is None and evaluation:
            relevance = getattr(evaluation, "overall_score", None)

        outcome = getattr(evaluation, "eligibility_outcome", None) or getattr(evaluation, "outcome", None) if evaluation else None
        eligibility = outcome.value if hasattr(outcome, "value") else str(outcome or "unknown")
        policy_state = "passed" if (evaluation and evaluation.hard_policy_passed) else "violation"

        if entry:
            # Preserve user overrides if set
            prev_state = {
                "priority": entry.priority,
                "queue_status": entry.queue_status,
                "relevance_score": entry.relevance_score,
                "ready_for_preparation": entry.ready_for_preparation,
            }

            if not entry.user_action:
                entry.priority = priority.value
                entry.queue_status = queue_status.value

            entry.match_evaluation_id = eval_id
            entry.eligibility_state = eligibility
            entry.policy_state = policy_state
            entry.review_requirements_json = reviews
            entry.job_availability = canonical_job.get("status") or "active"
            entry.relevance_score = relevance
            entry.ready_for_preparation = readiness
            entry.stage31_candidate_json = candidate.model_dump(mode="json") if candidate else None
            entry.version += 1
            entry.updated_at = datetime.now(UTC)

            # Log history
            self._log_history(
                queue_entry_id=entry.id,
                event_type="refreshed",
                previous_state=prev_state,
                new_state={
                    "priority": entry.priority,
                    "queue_status": entry.queue_status,
                    "relevance_score": entry.relevance_score,
                    "ready_for_preparation": entry.ready_for_preparation,
                },
                reason="Match evaluation or job details refreshed",
                session=session,
            )
            await session.flush()
            return self._to_queue_data(entry, canonical_job)

        # Create new entry
        entry = RecruitmentOpportunityQueueModel(
            canonical_job_id=job_id,
            applicant_profile_id=applicant_profile_id,
            career_strategy_id=career_strategy_id,
            match_evaluation_id=eval_id,
            priority=priority.value,
            queue_status=queue_status.value,
            eligibility_state=eligibility,
            policy_state=policy_state,
            review_requirements_json=reviews,
            job_availability=canonical_job.get("status") or "active",
            deadline=None,
            relevance_score=relevance,
            ready_for_preparation=readiness,
            stage31_candidate_json=candidate.model_dump(mode="json") if candidate else None,
            version=1,
        )
        session.add(entry)
        await session.flush()

        self._log_history(
            queue_entry_id=entry.id,
            event_type="created",
            previous_state={},
            new_state={
                "priority": entry.priority,
                "queue_status": entry.queue_status,
                "relevance_score": entry.relevance_score,
            },
            reason="Newly discovered canonical opportunity queued",
            session=session,
        )

        return self._to_queue_data(entry, canonical_job)

    async def get_entry(self, entry_id: str, session: AsyncSession) -> OpportunityQueueEntryData:
        stmt = (
            select(RecruitmentOpportunityQueueModel, JobListing)
            .join(JobListing, RecruitmentOpportunityQueueModel.canonical_job_id == JobListing.id)
            .where(RecruitmentOpportunityQueueModel.id == entry_id)
        )
        res = await session.execute(stmt)
        row = res.first()
        if not row:
            raise QueueEntryNotFoundError(f"Opportunity queue entry '{entry_id}' not found.")
        entry, job = row
        return self._to_queue_data(entry, self._job_to_dict(job))

    async def list_entries(
        self,
        applicant_profile_id: str,
        session: AsyncSession,
        priority: Optional[str] = None,
        queue_status: Optional[str] = None,
        ready_for_preparation: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[OpportunityQueueEntryData]:
        stmt = (
            select(RecruitmentOpportunityQueueModel, JobListing)
            .join(JobListing, RecruitmentOpportunityQueueModel.canonical_job_id == JobListing.id)
            .where(RecruitmentOpportunityQueueModel.applicant_profile_id == applicant_profile_id)
        )
        if priority:
            stmt = stmt.where(RecruitmentOpportunityQueueModel.priority == priority)
        if queue_status:
            stmt = stmt.where(RecruitmentOpportunityQueueModel.queue_status == queue_status)
        if ready_for_preparation is not None:
            stmt = stmt.where(RecruitmentOpportunityQueueModel.ready_for_preparation == ready_for_preparation)

        stmt = stmt.order_by(
            RecruitmentOpportunityQueueModel.priority.desc(),
            RecruitmentOpportunityQueueModel.relevance_score.desc().nullslast(),
            RecruitmentOpportunityQueueModel.created_at.desc(),
        ).limit(limit).offset(offset)

        res = await session.execute(stmt)
        rows = list(res.all())
        return [self._to_queue_data(entry, self._job_to_dict(job)) for entry, job in rows]

    async def update_entry(
        self,
        entry_id: str,
        req: OpportunityQueueUpdateRequest,
        session: AsyncSession,
    ) -> OpportunityQueueEntryData:
        stmt = (
            select(RecruitmentOpportunityQueueModel, JobListing)
            .join(JobListing, RecruitmentOpportunityQueueModel.canonical_job_id == JobListing.id)
            .where(RecruitmentOpportunityQueueModel.id == entry_id)
        )
        res = await session.execute(stmt)
        row = res.first()
        if not row:
            raise QueueEntryNotFoundError(f"Opportunity queue entry '{entry_id}' not found.")
        entry, job = row

        prev_state = {"priority": entry.priority, "status": entry.queue_status}

        if req.priority:
            entry.priority = req.priority.value
        if req.queue_status:
            entry.queue_status = req.queue_status.value
        if req.user_action:
            entry.user_action = req.user_action
            entry.user_action_at = datetime.now(UTC)
            if req.user_action == "save":
                entry.queue_status = OpportunityQueueStatus.SAVED.value
            elif req.user_action == "prioritize":
                entry.priority = OpportunityPriority.HIGH.value
            elif req.user_action == "deprioritize":
                entry.priority = OpportunityPriority.LOW.value
            elif req.user_action == "defer":
                entry.queue_status = OpportunityQueueStatus.DEFERRED.value
            elif req.user_action == "exclude":
                entry.queue_status = OpportunityQueueStatus.EXCLUDED.value
            elif req.user_action == "archive":
                entry.queue_status = OpportunityQueueStatus.ARCHIVED.value

        entry.version += 1
        entry.updated_at = datetime.now(UTC)

        self._log_history(
            queue_entry_id=entry.id,
            event_type="user_override" if req.user_action else "updated",
            previous_state=prev_state,
            new_state={"priority": entry.priority, "status": entry.queue_status},
            reason=f"User action: {req.user_action}" if req.user_action else "Queue entry updated",
            session=session,
        )

        await session.flush()
        return self._to_queue_data(entry, self._job_to_dict(job))

    def _calculate_priority(self, evaluation: Optional[JobMatchEvaluation]) -> OpportunityPriority:
        if not evaluation:
            return OpportunityPriority.NORMAL

        if not evaluation.hard_policy_passed:
            return OpportunityPriority.EXCLUDED

        has_reviews = bool(getattr(evaluation, "review_requests", None) or getattr(evaluation, "review_items", None))
        if has_reviews:
            return OpportunityPriority.CRITICAL_REVIEW

        score = getattr(evaluation, "relevance_index", None)
        if score is None:
            score = getattr(evaluation, "overall_score", 0.0)

        if score >= 80.0:
            return OpportunityPriority.HIGH
        elif score >= 60.0:
            return OpportunityPriority.NORMAL
        else:
            return OpportunityPriority.LOW

    def _calculate_queue_status(
        self,
        evaluation: Optional[JobMatchEvaluation],
        canonical_job: dict[str, Any],
    ) -> OpportunityQueueStatus:
        status = (canonical_job.get("status") or "active").lower()
        if status in ("closed", "expired", "removed"):
            return OpportunityQueueStatus.CLOSED

        if not evaluation:
            return OpportunityQueueStatus.AWAITING_MATCH

        if not evaluation.hard_policy_passed:
            return OpportunityQueueStatus.EXCLUDED

        has_reviews = bool(getattr(evaluation, "review_requests", None) or getattr(evaluation, "review_items", None))
        if has_reviews:
            return OpportunityQueueStatus.NEEDS_REVIEW

        score = getattr(evaluation, "relevance_index", None)
        if score is None:
            score = getattr(evaluation, "overall_score", 0.0)

        if score >= 80.0:
            return OpportunityQueueStatus.HIGH_PRIORITY
        elif score >= 60.0:
            return OpportunityQueueStatus.RECOMMENDED
        else:
            return OpportunityQueueStatus.DEFERRED

    def _log_history(
        self,
        queue_entry_id: str,
        event_type: str,
        previous_state: dict[str, Any],
        new_state: dict[str, Any],
        reason: Optional[str],
        session: AsyncSession,
    ) -> None:
        rec = RecruitmentOpportunityQueueHistoryModel(
            queue_entry_id=queue_entry_id,
            event_type=event_type,
            previous_state_json=previous_state,
            new_state_json=new_state,
            reason=reason,
        )
        session.add(rec)

    def _job_to_dict(self, job: JobListing) -> dict[str, Any]:
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "employment_type": job.employment_type,
            "work_arrangement": job.work_arrangement,
            "salary_range": job.salary_range,
            "application_url": job.application_url,
            "status": job.status,
        }

    def _to_queue_data(
        self,
        entry: RecruitmentOpportunityQueueModel,
        job_data: dict[str, Any],
    ) -> OpportunityQueueEntryData:
        candidate = None
        if entry.stage31_candidate_json:
            candidate = OpportunityPreparationCandidate(**entry.stage31_candidate_json)

        return OpportunityQueueEntryData(
            id=entry.id,
            canonical_job_id=entry.canonical_job_id,
            job_title=job_data.get("title") or "Unknown Title",
            company=job_data.get("company") or "Unknown Company",
            location=job_data.get("location"),
            employment_type=job_data.get("employment_type"),
            work_arrangement=job_data.get("work_arrangement"),
            salary_range=job_data.get("salary_range"),
            application_url=job_data.get("application_url") or "",
            applicant_profile_id=entry.applicant_profile_id,
            career_strategy_id=entry.career_strategy_id,
            match_evaluation_id=entry.match_evaluation_id,
            priority=OpportunityPriority(entry.priority),
            queue_status=OpportunityQueueStatus(entry.queue_status),
            eligibility_state=entry.eligibility_state,
            policy_state=entry.policy_state,
            review_requirements=entry.review_requirements_json or [],
            job_availability=entry.job_availability,
            deadline=entry.deadline,
            relevance_score=entry.relevance_score,
            user_action=entry.user_action,
            user_action_at=entry.user_action_at,
            ready_for_preparation=entry.ready_for_preparation,
            stage31_candidate=candidate,
            version=entry.version,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )


opportunity_queue_manager = OpportunityQueueManager()
