"""What-If scenario simulator for Stage 29 Matching Engine."""

from __future__ import annotations

import copy
import logging
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    MatchingOutcome,
    SimulationRequest,
    SimulationResponse,
    SkillGapItem,
    generate_uuid,
)
from app.recruitment.matching.decisions.matcher import evaluate_job_match

logger = logging.getLogger("autonom.recruitment.matching.decisions.simulation")


def run_what_if_simulation(
    original_evaluation_data: dict,
    canonical_job: dict,
    job_intelligence: JobIntelligenceSnapshotData,
    base_applicant_snapshot: ApplicantSnapshotData,
    base_career_strategy: CareerStrategySnapshotData,
    request: SimulationRequest,
) -> SimulationResponse:
    """Executes a hypothetical simulation without mutating underlying database records (Section 91, Required Test 154)."""
    # 1. Clone inputs to ensure absolute data isolation
    hypo_applicant = copy.deepcopy(base_applicant_snapshot)
    hypo_strategy = copy.deepcopy(base_career_strategy)

    # 2. Apply hypothetical adjustments
    if request.hypothetical_skills:
        for skill in request.hypothetical_skills:
            norm = skill.lower().strip()
            hypo_applicant.skills.append({
                "id": f"hypo_skill_{norm}",
                "name": skill,
                "canonical_name": norm,
                "category": "technical",
                "proficiency": "advanced",
                "years_experience": 3.0,
                "verification_status": "simulated",
                "is_verified": True,
                "evidence_refs": [],
            })

    if request.hypothetical_min_salary is not None:
        hypo_strategy.min_annual_salary = request.hypothetical_min_salary

    if request.hypothetical_work_arrangement:
        hypo_strategy.work_arrangements = [request.hypothetical_work_arrangement]

    if request.hypothetical_confirm_work_auth is not None:
        if request.hypothetical_confirm_work_auth:
            hypo_applicant.authorized_countries = ["US", "GLOBAL"]
        else:
            hypo_applicant.authorized_countries = []

    if request.hypothetical_graduation_status:
        if hypo_applicant.education:
            hypo_applicant.education[0]["academic_status"] = request.hypothetical_graduation_status

    # 3. Re-run deterministic matching pipeline on hypothetical snapshot
    sim_eval = evaluate_job_match(
        applicant_snapshot=hypo_applicant,
        canonical_job=canonical_job,
        job_intelligence=job_intelligence,
        career_strategy=hypo_strategy,
    )

    # 4. Compute differences
    orig_rel = original_evaluation_data.get("relevance_index", 0.0)
    orig_elig = MatchingOutcome(original_evaluation_data.get("eligibility_outcome", "not_evaluated"))

    diff_points = sim_eval.relevance_index - orig_rel
    diff_exp = (
        f"Simulated scenario '{request.scenario_name}': Relevance changed from {orig_rel:.1f} to "
        f"{sim_eval.relevance_index:.1f} ({'+' if diff_points >= 0 else ''}{diff_points:.1f} pts). "
        f"Eligibility shifted from '{orig_elig.value}' to '{sim_eval.eligibility_outcome.value}'."
    )

    dimension_diffs: list[dict] = []
    orig_scores = original_evaluation_data.get("score_breakdown", {}).get("dimensions", [])
    orig_map = {d.get("dimension_id"): d.get("raw_score", 0.0) for d in orig_scores}

    for d in sim_eval.score_breakdown.dimensions:
        before = orig_map.get(d.dimension_id, 0.0)
        after = d.raw_score
        if abs(before - after) > 0.001:
            dimension_diffs.append({
                "dimension_id": d.dimension_id,
                "name": d.name,
                "before_score": before,
                "after_score": after,
                "diff": round(after - before, 3),
            })

    return SimulationResponse(
        simulation_id=generate_uuid(),
        evaluation_id=request.evaluation_id,
        scenario_name=request.scenario_name,
        original_relevance_index=orig_rel,
        simulated_relevance_index=sim_eval.relevance_index,
        original_eligibility=orig_elig,
        simulated_eligibility=sim_eval.eligibility_outcome,
        diff_explanation=diff_exp,
        dimension_diffs=dimension_diffs,
        remaining_gaps=sim_eval.gaps,
    )
