"""Internal agent capabilities for Applicant-to-Job Matching Engine (Stage 29).

Registers typed callable capabilities for autonomous recruitment agents:
- JobMatchingAgent
- VerificationAgent
- ResumeAgent
- RecruitmentWritingAgent
- Supervisor
"""

from typing import Any
from app.recruitment.matching.contracts import SimulationRequest
from app.recruitment.matching.service import job_matching_service


async def capability_evaluate_job(
    canonical_job_id: str,
    profile_id: str | None = None,
    career_strategy_id: str | None = None,
    rubric_id: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Execute matching evaluation for a single canonical job against applicant facts."""
    ev = await job_matching_service.evaluate_job(
        canonical_job_id=canonical_job_id,
        profile_id=profile_id,
        career_strategy_id=career_strategy_id,
        rubric_id=rubric_id,
        force=force,
    )
    return ev.model_dump(mode="json")


async def capability_evaluate_batch(
    job_ids: list[str],
    profile_id: str | None = None,
    career_strategy_id: str | None = None,
    rubric_id: str | None = None,
    force: bool = False,
) -> list[dict[str, Any]]:
    """Execute batch matching evaluations for a set of candidate jobs."""
    results = await job_matching_service.evaluate_batch(
        job_ids=job_ids,
        profile_id=profile_id,
        career_strategy_id=career_strategy_id,
        rubric_id=rubric_id,
        force=force,
    )
    return [r.model_dump(mode="json") for r in results]


async def capability_get_result(evaluation_id: str) -> dict[str, Any] | None:
    """Fetch complete evaluation record by ID."""
    ev = await job_matching_service.get_evaluation(evaluation_id)
    return ev.model_dump(mode="json") if ev else None


async def capability_get_eligibility(evaluation_id: str) -> dict[str, Any] | None:
    """Fetch eligibility decision and condition details."""
    ev = await job_matching_service.get_evaluation(evaluation_id)
    if not ev:
        return None
    return {
        "evaluation_id": ev.id,
        "canonical_job_id": ev.canonical_job_id,
        "eligibility_outcome": ev.eligibility_outcome.value,
        "hard_policy_passed": ev.hard_policy_passed,
        "hard_policy_reason": ev.hard_policy_reason,
        "readiness": ev.application_readiness.value,
        "eligibility_detail": ev.eligibility_detail.model_dump(mode="json"),
    }


async def capability_get_requirement_coverage(evaluation_id: str) -> dict[str, Any] | None:
    """Fetch requirement-by-requirement evaluation matrix."""
    ev = await job_matching_service.get_evaluation(evaluation_id)
    if not ev:
        return None
    return {
        "mandatory_coverage_ratio": ev.mandatory_coverage_ratio,
        "preferred_coverage_ratio": ev.preferred_coverage_ratio,
        "requirements": [r.model_dump(mode="json") for r in ev.requirement_results],
        "groups": [g.model_dump(mode="json") for g in ev.group_results],
    }


async def capability_get_skill_gaps(evaluation_id: str) -> list[dict[str, Any]]:
    """Fetch identified qualification gaps and remediation suggestions."""
    ev = await job_matching_service.get_evaluation(evaluation_id)
    if not ev:
        return []
    return [g.model_dump(mode="json") for g in ev.gaps]


async def capability_get_evidence(evaluation_id: str) -> list[dict[str, Any]]:
    """Fetch evidence snippets attached to requirement evaluations."""
    ev = await job_matching_service.get_evaluation(evaluation_id)
    if not ev:
        return []
    return [
        {
            "requirement_id": r.requirement_id,
            "name": r.name,
            "claim_ref": r.applicant_claim_ref,
            "applicant_snippet": r.applicant_evidence_snippet,
            "job_snippet": r.job_evidence_snippet,
            "confidence": r.confidence,
        }
        for r in ev.requirement_results
        if r.applicant_evidence_snippet
    ]


async def capability_get_ranking(
    profile_id: str | None = None,
    strategy_id: str | None = None,
    rubric_id: str | None = None,
) -> dict[str, Any]:
    """Fetch ranked opportunities and overview metrics."""
    ranked_items, overview = await job_matching_service.get_rankings(
        profile_id=profile_id,
        strategy_id=strategy_id,
        rubric_id=rubric_id,
    )
    return {
        "items": [item.model_dump(mode="json") for item in ranked_items],
        "overview": overview.model_dump(mode="json"),
    }


async def capability_explain_result(evaluation_id: str) -> dict[str, Any] | None:
    """Fetch transparent relevance index breakdown and score dimension explanations."""
    ev = await job_matching_service.get_evaluation(evaluation_id)
    if not ev:
        return None
    return {
        "relevance_index": ev.relevance_index,
        "summary": ev.summary_explanation,
        "score_breakdown": ev.score_breakdown.model_dump(mode="json"),
        "counterfactuals": [c.model_dump(mode="json") for c in ev.counterfactuals],
    }


async def capability_compare_jobs(
    canonical_job_ids: list[str],
    profile_id: str | None = None,
) -> dict[str, Any]:
    """Generate side-by-side comparison matrix for multiple jobs."""
    matrix = await job_matching_service.compare_jobs(canonical_job_ids, profile_id=profile_id)
    return matrix.model_dump(mode="json")


async def capability_get_review_queue() -> list[dict[str, Any]]:
    """Fetch pending human review items."""
    return await job_matching_service.get_review_queue()


async def capability_simulate(
    evaluation_id: str,
    scenario_name: str,
    hypothetical_skills: list[str] | None = None,
    hypothetical_min_salary: float | None = None,
    hypothetical_work_arrangement: str | None = None,
    hypothetical_confirm_work_auth: bool | None = None,
) -> dict[str, Any]:
    """Execute What-If simulation without persisting changes to source profile or active policy."""
    req = SimulationRequest(
        evaluation_id=evaluation_id,
        scenario_name=scenario_name,
        hypothetical_skills=hypothetical_skills or [],
        hypothetical_min_salary=hypothetical_min_salary,
        hypothetical_work_arrangement=hypothetical_work_arrangement,
        hypothetical_confirm_work_auth=hypothetical_confirm_work_auth,
    )
    res = await job_matching_service.simulate(req)
    return res.model_dump(mode="json")


async def capability_get_history(profile_id: str | None = None) -> list[dict[str, Any]]:
    """Fetch historical evaluations including stale versions."""
    evals = await job_matching_service.list_evaluations(profile_id=profile_id, is_current_only=False)
    return [e.model_dump(mode="json") for e in evals]
