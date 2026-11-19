"""Authoritative Applicant-to-Job Matching and Prioritization Service for AUTONOM (Stage 29)."""

from __future__ import annotations

import logging
from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.engine import get_db_session
from app.db.models import (
    JobMatchEvaluationModel,
    JobMatchGapModel,
    JobMatchLogicalGroupResultModel,
    JobMatchRequirementResultModel,
    JobMatchReviewRequestModel,
    JobMatchRubricModel,
    JobMatchSimulationModel,
)
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    DimensionScore,
    EducationMatchDetail,
    EligibilityConditionDetail,
    ExperienceMatchDetail,
    GroupEvaluationResult,
    JobComparisonMatrix,
    JobIntelligenceSnapshotData,
    JobMatchEvaluation,
    MatchingOutcome,
    RankedOpportunityItem,
    RankingOverview,
    RelevanceIndexBreakdown,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    RubricConfig,
    SimulationRequest,
    SimulationResponse,
    SkillGapItem,
    SkillMatchDetail,
)
from app.recruitment.matching.decisions.comparison import build_comparison_matrix
from app.recruitment.matching.decisions.matcher import evaluate_job_match
from app.recruitment.matching.decisions.simulation import run_what_if_simulation
from app.recruitment.matching.errors import (
    CanonicalJobNotFoundError,
    EvaluationNotFoundError,
    JobIntelligenceNotFoundError,
)
from app.recruitment.matching.inputs.applicant_snapshot import resolve_applicant_snapshot
from app.recruitment.matching.inputs.canonical_jobs import resolve_canonical_job
from app.recruitment.matching.inputs.career_policy import resolve_career_policy
from app.recruitment.matching.inputs.job_intelligence import resolve_job_intelligence
from app.recruitment.matching.lifecycle.caching import (
    generate_cache_key,
    get_cached_evaluation,
    set_cached_evaluation,
)
from app.recruitment.matching.ranking.prioritization import rank_opportunities
from app.recruitment.matching.ranking.rubric import get_rubric

logger = logging.getLogger("autonom.recruitment.matching.service")


class JobMatchingService:
    """Master facade for applicant-to-job matching, qualification evaluation, and opportunity ranking."""

    def __init__(self) -> None:
        self._in_memory_evaluations: dict[str, JobMatchEvaluation] = {}

    async def evaluate_job(
        self,
        canonical_job_id: str,
        profile_id: str | None = None,
        career_strategy_id: str | None = None,
        rubric_id: str | None = None,
        force: bool = False,
        use_ai: bool = False,
        db_session: AsyncSession | None = None,
    ) -> JobMatchEvaluation:
        """Executes comprehensive matching evaluation for a single canonical job against applicant profile."""
        if db_session is not None:
            return await self._evaluate_job_with_session(
                canonical_job_id=canonical_job_id,
                profile_id=profile_id,
                career_strategy_id=career_strategy_id,
                rubric_id=rubric_id,
                force=force,
                db_session=db_session,
            )

        async with get_db_session() as session:
            return await self._evaluate_job_with_session(
                canonical_job_id=canonical_job_id,
                profile_id=profile_id,
                career_strategy_id=career_strategy_id,
                rubric_id=rubric_id,
                force=force,
                db_session=session,
            )

    async def _evaluate_job_with_session(
        self,
        canonical_job_id: str,
        profile_id: str | None,
        career_strategy_id: str | None,
        rubric_id: str | None,
        force: bool,
        db_session: AsyncSession,
    ) -> JobMatchEvaluation:
        # 1. Resolve inputs
        applicant_snapshot = resolve_applicant_snapshot(profile_id)
        career_strategy = resolve_career_policy(career_strategy_id)
        canonical_job = await resolve_canonical_job(canonical_job_id, db_session)
        job_intelligence = await resolve_job_intelligence(canonical_job_id, db_session)
        rubric = get_rubric(rubric_id)

        # 2. Check deterministic cache if not force
        cache_key = generate_cache_key(applicant_snapshot, job_intelligence, career_strategy, rubric)
        if not force:
            cached = get_cached_evaluation(cache_key)
            if cached:
                return cached

        # 3. Execute deterministic matching pipeline
        evaluation = evaluate_job_match(
            applicant_snapshot=applicant_snapshot,
            canonical_job=canonical_job,
            job_intelligence=job_intelligence,
            career_strategy=career_strategy,
            rubric=rubric,
        )

        # 4. Mark prior evaluations for this job & profile as not current
        await db_session.execute(
            update(JobMatchEvaluationModel)
            .where(
                JobMatchEvaluationModel.canonical_job_id == canonical_job_id,
                JobMatchEvaluationModel.profile_id == applicant_snapshot.profile_id,
                JobMatchEvaluationModel.is_current == True,  # noqa: E712
            )
            .values(is_current=False)
        )

        # 5. Persist to database
        await self._persist_evaluation_in_db(evaluation, db_session)

        # 6. Update cache & memory
        set_cached_evaluation(cache_key, evaluation)
        self._in_memory_evaluations[evaluation.id] = evaluation

        return evaluation

    async def _persist_evaluation_in_db(
        self,
        evaluation: JobMatchEvaluation,
        session: AsyncSession,
    ) -> None:
        """Persists relational evaluation records and children to SQLite."""
        score_comp_dump = evaluation.score_breakdown.model_dump(mode="json")
        gaps_dump = [g.model_dump(mode="json") for g in evaluation.gaps]

        eval_model = JobMatchEvaluationModel(
            id=evaluation.id,
            profile_id=evaluation.profile_id,
            canonical_job_id=evaluation.canonical_job_id,
            job_intelligence_id=None,
            career_strategy_id=evaluation.career_strategy_id,
            rubric_id=evaluation.rubric_id,
            version=evaluation.version,
            is_current=True,
            status=evaluation.status,
            eligibility_outcome=evaluation.eligibility_outcome.value,
            relevance_index=evaluation.relevance_index,
            mandatory_coverage_ratio=evaluation.mandatory_coverage_ratio,
            preferred_coverage_ratio=evaluation.preferred_coverage_ratio,
            evidence_completeness_ratio=evaluation.evidence_completeness_ratio,
            ranking_uncertainty_ratio=evaluation.ranking_uncertainty_ratio,
            application_readiness=evaluation.application_readiness.value,
            hard_policy_passed=evaluation.hard_policy_passed,
            hard_policy_reason=evaluation.hard_policy_reason,
            summary_explanation=evaluation.summary_explanation,
            score_components_json=score_comp_dump,
            input_snapshots_json={},
            gaps_summary_json=gaps_dump,
            recommendation_tags_json=[],
            evaluated_at=evaluation.evaluated_at,
            updated_at=evaluation.updated_at,
        )
        session.add(eval_model)

        # Persist requirements
        for req in evaluation.requirement_results:
            req_model = JobMatchRequirementResultModel(
                id=f"res_{evaluation.id[:8]}_{req.requirement_id[:20]}",
                evaluation_id=evaluation.id,
                requirement_id=req.requirement_id,
                requirement_name=req.name,
                requirement_category=req.category,
                match_category=req.match_category.value,
                applicant_claim_ref=req.applicant_claim_ref,
                applicant_evidence_snippet=req.applicant_evidence_snippet,
                job_evidence_snippet=req.job_evidence_snippet,
                confidence=req.confidence,
                explanation=req.explanation,
                is_satisfied=req.is_satisfied,
            )
            session.add(req_model)

        # Persist groups
        for grp in evaluation.group_results:
            grp_model = JobMatchLogicalGroupResultModel(
                id=f"res_grp_{evaluation.id[:8]}_{grp.group_id[:20]}",
                evaluation_id=evaluation.id,
                group_id=grp.group_id,
                operator=grp.operator,
                target_count=grp.target_count,
                satisfied_count=grp.satisfied_count,
                is_satisfied=grp.is_satisfied,
                is_unknown=grp.is_unknown,
                explanation=grp.explanation,
            )
            session.add(grp_model)

        # Persist gaps
        for g in evaluation.gaps:
            gap_model = JobMatchGapModel(
                id=g.id,
                evaluation_id=evaluation.id,
                requirement_id=g.requirement_id,
                gap_type=g.gap_type.value,
                severity=g.severity.value,
                skill_or_qualification=g.skill_or_qualification,
                description=g.description,
                remediation_suggestion=g.remediation_suggestion,
            )
            session.add(gap_model)

        # Persist review requests
        for rev in evaluation.review_requests:
            rev_model = JobMatchReviewRequestModel(
                id=rev.get("id", f"rev_{evaluation.id[:8]}"),
                evaluation_id=evaluation.id,
                review_type=rev.get("review_type", "unknown_mandatory_qualification"),
                trigger_reason=rev.get("trigger_reason", ""),
                status=rev.get("status", "pending"),
            )
            session.add(rev_model)

        await session.flush()

    async def evaluate_batch(
        self,
        job_ids: list[str],
        profile_id: str | None = None,
        career_strategy_id: str | None = None,
        rubric_id: str | None = None,
        force: bool = False,
        db_session: AsyncSession | None = None,
    ) -> list[JobMatchEvaluation]:
        """Evaluates a batch of canonical jobs sequentially and transactional."""
        results: list[JobMatchEvaluation] = []
        if db_session is not None:
            for jid in job_ids:
                try:
                    ev = await self._evaluate_job_with_session(jid, profile_id, career_strategy_id, rubric_id, force, db_session)
                    results.append(ev)
                except Exception as exc:
                    logger.warning(f"Batch evaluation error on job '{jid}': {exc}")
            return results

        async with get_db_session() as session:
            for jid in job_ids:
                try:
                    ev = await self._evaluate_job_with_session(jid, profile_id, career_strategy_id, rubric_id, force, session)
                    results.append(ev)
                except Exception as exc:
                    logger.warning(f"Batch evaluation error on job '{jid}': {exc}")
        return results

    async def get_evaluation(
        self,
        evaluation_id: str,
        db_session: AsyncSession | None = None,
    ) -> JobMatchEvaluation | None:
        """Retrieves an existing evaluation by evaluation ID."""
        if evaluation_id in self._in_memory_evaluations:
            return self._in_memory_evaluations[evaluation_id]

        if db_session is not None:
            return await self._load_evaluation_from_db(evaluation_id, db_session)

        async with get_db_session() as session:
            return await self._load_evaluation_from_db(evaluation_id, session)

    async def _load_evaluation_from_db(
        self,
        evaluation_id: str,
        session: AsyncSession,
    ) -> JobMatchEvaluation | None:
        stmt = (
            select(JobMatchEvaluationModel)
            .options(
                selectinload(JobMatchEvaluationModel.requirements),
                selectinload(JobMatchEvaluationModel.groups),
                selectinload(JobMatchEvaluationModel.gaps),
                selectinload(JobMatchEvaluationModel.review_requests),
                selectinload(JobMatchEvaluationModel.job),
            )
            .where(JobMatchEvaluationModel.id == evaluation_id)
        )
        res = await session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            return None

        return self._convert_model_to_evaluation(model)

    def _convert_model_to_evaluation(self, model: JobMatchEvaluationModel) -> JobMatchEvaluation:
        """Converts SQLAlchemy model to strongly typed Pydantic contract."""
        score_dump = model.score_components_json or {}
        breakdown = RelevanceIndexBreakdown.model_validate(score_dump) if score_dump else RelevanceIndexBreakdown(relevance_index=model.relevance_index)

        reqs: list[RequirementEvaluationResult] = [
            RequirementEvaluationResult(
                requirement_id=r.requirement_id,
                name=r.requirement_name,
                category=r.requirement_category,
                match_category=RequirementMatchCategory(r.match_category),
                applicant_claim_ref=r.applicant_claim_ref,
                applicant_evidence_snippet=r.applicant_evidence_snippet,
                job_evidence_snippet=r.job_evidence_snippet,
                confidence=r.confidence,
                explanation=r.explanation or "",
                is_satisfied=r.is_satisfied,
            )
            for r in model.requirements
        ]

        grps: list[GroupEvaluationResult] = [
            GroupEvaluationResult(
                group_id=g.group_id,
                operator=g.operator,
                target_count=g.target_count,
                satisfied_count=g.satisfied_count,
                is_satisfied=g.is_satisfied,
                is_unknown=g.is_unknown,
                explanation=g.explanation or "",
            )
            for g in model.groups
        ]

        gaps: list[SkillGapItem] = [
            SkillGapItem(
                id=gap.id,
                requirement_id=gap.requirement_id,
                skill_or_qualification=gap.skill_or_qualification,
                gap_type=gap.gap_type,
                severity=gap.severity,
                description=gap.description,
                remediation_suggestion=gap.remediation_suggestion or "",
            )
            for gap in model.gaps
        ]

        job = model.job
        return JobMatchEvaluation(
            id=model.id,
            profile_id=model.profile_id,
            canonical_job_id=model.canonical_job_id,
            job_title=job.title if job else "Untitled",
            company_name=job.company if job else "Employer",
            job_location=job.location if job else None,
            employment_type=job.employment_type if job else None,
            work_arrangement=job.work_arrangement if job else None,
            career_strategy_id=model.career_strategy_id,
            rubric_id=model.rubric_id,
            version=model.version,
            is_current=model.is_current,
            status=model.status,
            eligibility_outcome=MatchingOutcome(model.eligibility_outcome),
            relevance_index=model.relevance_index,
            mandatory_coverage_ratio=model.mandatory_coverage_ratio,
            preferred_coverage_ratio=model.preferred_coverage_ratio,
            evidence_completeness_ratio=model.evidence_completeness_ratio,
            ranking_uncertainty_ratio=model.ranking_uncertainty_ratio,
            application_readiness=model.application_readiness,
            hard_policy_passed=model.hard_policy_passed,
            hard_policy_reason=model.hard_policy_reason,
            summary_explanation=model.summary_explanation or "",
            requirement_results=reqs,
            group_results=grps,
            skill_details=[],
            education_detail=None,
            experience_detail=None,
            score_breakdown=breakdown,
            gaps=gaps,
            missing_information=[],
            review_requests=[{"id": r.id, "review_type": r.review_type, "trigger_reason": r.trigger_reason, "status": r.status} for r in model.review_requests],
            counterfactuals=[],
            evaluated_at=model.evaluated_at,
            updated_at=model.updated_at,
        )

    async def list_evaluations(
        self,
        profile_id: str | None = None,
        is_current_only: bool = True,
        db_session: AsyncSession | None = None,
    ) -> list[JobMatchEvaluation]:
        """Lists match evaluations filtered by profile and currency."""
        if db_session is not None:
            return await self._list_evaluations_with_session(profile_id, is_current_only, db_session)

        async with get_db_session() as session:
            return await self._list_evaluations_with_session(profile_id, is_current_only, session)

    async def _list_evaluations_with_session(
        self,
        profile_id: str | None,
        is_current_only: bool,
        session: AsyncSession,
    ) -> list[JobMatchEvaluation]:
        stmt = select(JobMatchEvaluationModel).options(
            selectinload(JobMatchEvaluationModel.requirements),
            selectinload(JobMatchEvaluationModel.groups),
            selectinload(JobMatchEvaluationModel.gaps),
            selectinload(JobMatchEvaluationModel.review_requests),
            selectinload(JobMatchEvaluationModel.job),
        )
        if profile_id:
            stmt = stmt.where(JobMatchEvaluationModel.profile_id == profile_id)
        if is_current_only:
            stmt = stmt.where(JobMatchEvaluationModel.is_current == True)  # noqa: E712

        stmt = stmt.order_by(JobMatchEvaluationModel.evaluated_at.desc())
        res = await session.execute(stmt)
        models = res.scalars().all()

        return [self._convert_model_to_evaluation(m) for m in models]

    async def get_rankings(
        self,
        profile_id: str | None = None,
        strategy_id: str | None = None,
        rubric_id: str | None = None,
        db_session: AsyncSession | None = None,
    ) -> tuple[list[RankedOpportunityItem], RankingOverview]:
        """Calculates prioritized opportunity rankings across current evaluated jobs."""
        evals = await self.list_evaluations(profile_id=profile_id, is_current_only=True, db_session=db_session)
        return rank_opportunities(evals)

    async def compare_jobs(
        self,
        canonical_job_ids: list[str],
        profile_id: str | None = None,
        db_session: AsyncSession | None = None,
    ) -> JobComparisonMatrix:
        """Generates side-by-side comparison matrix for selected canonical jobs."""
        evals: list[JobMatchEvaluation] = []
        for jid in canonical_job_ids:
            ev = await self.evaluate_job(canonical_job_id=jid, profile_id=profile_id, db_session=db_session)
            evals.append(ev)
        return build_comparison_matrix(evals)

    async def simulate(
        self,
        request: SimulationRequest,
        db_session: AsyncSession | None = None,
    ) -> SimulationResponse:
        """Executes What-If hypothetical simulation without profile or policy mutation (Required Test 154)."""
        ev = await self.get_evaluation(request.evaluation_id, db_session=db_session)
        if not ev:
            raise EvaluationNotFoundError(f"Evaluation '{request.evaluation_id}' not found.")

        # Resolve underlying inputs
        applicant_snapshot = resolve_applicant_snapshot(ev.profile_id)
        career_strategy = resolve_career_policy(ev.career_strategy_id)

        if db_session is not None:
            canonical_job = await resolve_canonical_job(ev.canonical_job_id, db_session)
            job_intelligence = await resolve_job_intelligence(ev.canonical_job_id, db_session)
        else:
            async with get_db_session() as session:
                canonical_job = await resolve_canonical_job(ev.canonical_job_id, session)
                job_intelligence = await resolve_job_intelligence(ev.canonical_job_id, session)

        orig_eval_data = ev.model_dump(mode="json")

        sim_response = run_what_if_simulation(
            original_evaluation_data=orig_eval_data,
            canonical_job=canonical_job,
            job_intelligence=job_intelligence,
            base_applicant_snapshot=applicant_snapshot,
            base_career_strategy=career_strategy,
            request=request,
        )

        # Record simulation history
        async with get_db_session() as session:
            sim_model = JobMatchSimulationModel(
                id=sim_response.simulation_id,
                evaluation_id=request.evaluation_id,
                scenario_name=request.scenario_name,
                hypothetical_adjustments_json={
                    "skills": request.hypothetical_skills,
                    "min_salary": request.hypothetical_min_salary,
                    "work_arrangement": request.hypothetical_work_arrangement,
                    "confirm_work_auth": request.hypothetical_confirm_work_auth,
                },
                original_relevance_index=sim_response.original_relevance_index,
                simulated_relevance_index=sim_response.simulated_relevance_index,
                original_eligibility=sim_response.original_eligibility.value,
                simulated_eligibility=sim_response.simulated_eligibility.value,
                diff_explanation=sim_response.diff_explanation,
            )
            session.add(sim_model)
            await session.commit()

        return sim_response

    async def get_review_queue(self, db_session: AsyncSession | None = None) -> list[dict[str, Any]]:
        """Returns pending review queue items."""
        if db_session is not None:
            return await self._get_review_queue_with_session(db_session)
        async with get_db_session() as session:
            return await self._get_review_queue_with_session(session)

    async def _get_review_queue_with_session(self, session: AsyncSession) -> list[dict[str, Any]]:
        stmt = (
            select(JobMatchReviewRequestModel)
            .where(JobMatchReviewRequestModel.status == "pending")
            .order_by(JobMatchReviewRequestModel.created_at.desc())
        )
        res = await session.execute(stmt)
        rows = res.scalars().all()
        return [
            {
                "id": r.id,
                "evaluation_id": r.evaluation_id,
                "review_type": r.review_type,
                "trigger_reason": r.trigger_reason,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]

    async def resolve_review(
        self,
        review_id: str,
        resolution_notes: str,
        decision: str,
        reviewer_id: str = "user",
        db_session: AsyncSession | None = None,
    ) -> bool:
        """Resolves or defers an item in the matching review queue."""
        if db_session is not None:
            return await self._resolve_review_with_session(review_id, resolution_notes, decision, reviewer_id, db_session)
        async with get_db_session() as session:
            return await self._resolve_review_with_session(review_id, resolution_notes, decision, reviewer_id, session)

    async def _resolve_review_with_session(
        self,
        review_id: str,
        resolution_notes: str,
        decision: str,
        reviewer_id: str,
        session: AsyncSession,
    ) -> bool:
        stmt = (
            update(JobMatchReviewRequestModel)
            .where(JobMatchReviewRequestModel.id == review_id)
            .values(
                status=decision,
                resolution_notes=resolution_notes,
                resolved_by=reviewer_id,
                resolved_at=utc_now(),
            )
        )
        res = await session.execute(stmt)
        return res.rowcount > 0


# Singleton instance
job_matching_service = JobMatchingService()
