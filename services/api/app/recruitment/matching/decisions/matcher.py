"""Master end-to-end evaluation pipeline for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.conditions import (
    evaluate_compensation,
    evaluate_employer_restrictions,
    evaluate_location,
    evaluate_relocation,
    evaluate_remote_compatibility,
    evaluate_sponsorship,
    evaluate_work_authorization,
)
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    CounterfactualScenario,
    EligibilityConditionDetail,
    JobIntelligenceSnapshotData,
    JobMatchEvaluation,
    MatchingOutcome,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    ReviewType,
    RubricConfig,
    generate_uuid,
    utc_now,
)
from app.recruitment.matching.eligibility import (
    determine_matching_outcome,
    evaluate_logical_groups,
)
from app.recruitment.matching.gaps import analyze_qualification_gaps
from app.recruitment.matching.inputs.evidence import resolve_evidence_map
from app.recruitment.matching.qualifications import (
    calculate_non_overlapping_duration,
    evaluate_certifications,
    evaluate_education,
    evaluate_experience,
    evaluate_licensing_and_clearances,
    evaluate_skills,
)
from app.recruitment.matching.ranking import compute_relevance_index, get_rubric

logger = logging.getLogger("autonom.recruitment.matching.decisions.matcher")


def evaluate_job_match(
    applicant_snapshot: ApplicantSnapshotData,
    canonical_job: dict[str, Any],
    job_intelligence: JobIntelligenceSnapshotData,
    career_strategy: CareerStrategySnapshotData,
    rubric: RubricConfig | None = None,
) -> JobMatchEvaluation:
    """Executes deterministic, evidence-backed evaluation of an applicant against a canonical job (Section 66)."""
    active_rubric = rubric or get_rubric()
    evidence_map = resolve_evidence_map(applicant_snapshot)
    atomic_results: list[RequirementEvaluationResult] = []

    hard_policy_passed = True
    hard_policy_reason: str | None = None

    # 1. Employer Restrictions (Blocklist) - Required Test 143
    is_blocked, block_reason = evaluate_employer_restrictions(
        canonical_job.get("company", ""),
        career_strategy,
    )
    if is_blocked:
        hard_policy_passed = False
        hard_policy_reason = block_reason

    # 2. Compensation Compatibility - Required Test 142
    comp_res, comp_factor, comp_violation, comp_reason = evaluate_compensation(
        job_intelligence.compensation,
        career_strategy,
    )
    if comp_res:
        atomic_results.append(comp_res)
    if comp_violation:
        hard_policy_passed = False
        hard_policy_reason = comp_reason

    # 3. Location and Relocation Compatibility
    loc_res, loc_violation, loc_reason = evaluate_location(
        canonical_job.get("location"),
        career_strategy,
        applicant_snapshot,
    )
    if loc_res:
        atomic_results.append(loc_res)
    if loc_violation:
        hard_policy_passed = False
        hard_policy_reason = loc_reason

    # 4. Remote Country Restrictions - Required Test 141
    remote_res, remote_violation, remote_reason = evaluate_remote_compatibility(
        job_intelligence.employment_conditions,
        canonical_job.get("location"),
        career_strategy,
        applicant_snapshot,
    )
    if remote_res:
        atomic_results.append(remote_res)
    if remote_violation:
        hard_policy_passed = False
        hard_policy_reason = remote_reason

    # 5. Work Authorization & Visa Sponsorship - Required Tests 139, 140
    work_auth_res, auth_conflict, auth_reason = evaluate_work_authorization(
        job_intelligence.eligibility,
        applicant_snapshot,
    )
    if work_auth_res:
        atomic_results.append(work_auth_res)
    if auth_conflict:
        hard_policy_passed = False
        hard_policy_reason = auth_reason

    sponsor_res, sponsor_conflict, sponsor_reason = evaluate_sponsorship(
        job_intelligence.eligibility,
        applicant_snapshot,
    )
    if sponsor_res:
        atomic_results.append(sponsor_res)
    if sponsor_conflict:
        hard_policy_passed = False
        hard_policy_reason = sponsor_reason

    # 6. Experience Duration & Overlap Calculation - Required Tests 136, 137
    prof_years, _, _ = calculate_non_overlapping_duration(applicant_snapshot.experience)
    exp_detail, exp_results = evaluate_experience(
        job_intelligence.experience,
        applicant_snapshot,
    )
    atomic_results.extend(exp_results)

    # 7. Education Prerequisites & Practical Waivers - Required Tests 134, 135
    edu_detail, edu_results = evaluate_education(
        job_intelligence.education,
        applicant_snapshot,
        professional_years=prof_years,
    )
    atomic_results.extend(edu_results)

    # 8. Skill Matching (Exact, Aliases, Tenure, Related Families)
    skill_details, skill_results = evaluate_skills(
        job_intelligence.skills,
        applicant_snapshot,
        evidence_map,
    )
    atomic_results.extend(skill_results)

    # 9. Certifications & Security Clearances
    cert_results = evaluate_certifications(
        job_intelligence.mandatory_requirements,
        applicant_snapshot,
    )
    atomic_results.extend(cert_results)

    clearance_results = evaluate_licensing_and_clearances(
        job_intelligence.eligibility,
        applicant_snapshot,
    )
    atomic_results.extend(clearance_results)

    # 10. Logical Groups (AND, OR, AtLeastN) - Required Tests 132, 133
    group_results = evaluate_logical_groups(
        job_intelligence.requirement_groups,
        atomic_results,
    )

    # Derive requirements covered by satisfied alternative groups (OR, AtLeastN, etc.)
    satisfied_alt_reqs: set[str] = set()
    for g in job_intelligence.requirement_groups:
        op = g.get("operator", "AND").upper()
        if op in ("OR", "EQUIVALENTALTERNATIVE", "ATLEASTN"):
            g_id = g.get("id")
            gres = next((gr for gr in group_results if gr.group_id == g_id), None)
            if gres and gres.is_satisfied:
                child_reqs = g.get("requirement_ids") or g.get("requirements") or g.get("child_requirement_ids") or []
                for cr in child_reqs:
                    name_or_id = cr.get("name", cr.get("id", "")) if isinstance(cr, dict) else str(cr)
                    if name_or_id:
                        satisfied_alt_reqs.add(name_or_id.lower())

    # 11. Metadata mapping for scoring
    has_disclosed_comp = bool(
        job_intelligence.compensation.get("salary_min")
        or job_intelligence.compensation.get("salary_max")
    )
    job_metadata = {
        "title": canonical_job.get("title", ""),
        "company": canonical_job.get("company", ""),
        "role_family": job_intelligence.role_family,
        "work_arrangement": canonical_job.get("work_arrangement"),
        "min_years_experience": job_intelligence.experience[0].get("min_years") if job_intelligence.experience else None,
        "has_disclosed_compensation": has_disclosed_comp,
        "discovered_at": canonical_job.get("discovered_at"),
    }

    # 12. Deterministic Relevance Index Computation
    score_breakdown, relevance_index, mandatory_ratio, preferred_ratio, uncertainty_ratio = compute_relevance_index(
        atomic_results=atomic_results,
        job_metadata=job_metadata,
        career_strategy=career_strategy,
        applicant_snapshot=applicant_snapshot,
        compensation_factor=comp_factor,
        professional_years=prof_years,
        rubric=active_rubric,
        satisfied_alt_reqs=satisfied_alt_reqs,
    )

    # 13. Gap Intelligence & Missing Information Requests
    gaps, missing_info = analyze_qualification_gaps(atomic_results, satisfied_alt_reqs=satisfied_alt_reqs)

    # 14. Synthesize Final Outcome & Application Readiness
    outcome, readiness, summary_exp = determine_matching_outcome(
        job_status=canonical_job.get("status", "active"),
        hard_policy_passed=hard_policy_passed,
        hard_policy_reason=hard_policy_reason,
        atomic_results=atomic_results,
        group_results=group_results,
        relevance_index=relevance_index,
        satisfied_alt_reqs=satisfied_alt_reqs,
    )

    # 15. Formulate Counterfactual Scenarios (Section 90)
    counterfactuals: list[CounterfactualScenario] = []
    if outcome == MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET:
        for g in gaps:
            if g.severity.value == "blocking":
                counterfactuals.append(CounterfactualScenario(
                    scenario_name=f"Bridge {g.skill_or_qualification}",
                    hypothetical_change=f"Acquire confirmed qualification for {g.skill_or_qualification}",
                    current_state="Ineligible (Mandatory requirement unmet)",
                    simulated_state="Potentially Eligible",
                    impact_summary=f"Resolving '{g.skill_or_qualification}' would eliminate blocking gap.",
                ))
    elif outcome == MatchingOutcome.REQUIRES_APPLICANT_REVIEW:
        counterfactuals.append(CounterfactualScenario(
            scenario_name="Confirm Work Authorization",
            hypothetical_change="Verify authorized country status in profile",
            current_state="Requires Review (Unknown authorization)",
            simulated_state="Eligible and Aligned",
            impact_summary="Explicitly confirming work authorization would remove review requirement.",
        ))

    # Review requests list
    review_requests: list[dict[str, Any]] = []
    for r in atomic_results:
        if r.match_category == RequirementMatchCategory.UNKNOWN and r.category == "mandatory":
            r_type = (
                ReviewType.UNKNOWN_WORK_AUTH.value
                if "work_authorization" in r.requirement_id.lower() or "authorization" in r.name.lower()
                else "unknown_mandatory_qualification"
            )
            review_requests.append({
                "id": f"rev_{r.requirement_id}",
                "review_type": r_type,
                "reason": r.explanation,
                "trigger_reason": r.explanation,
                "status": "pending",
                "created_at": utc_now().isoformat(),
            })

    eligibility_detail = EligibilityConditionDetail(
        work_authorization_status=work_auth_res.match_category.value if work_auth_res else "not_specified",
        sponsorship_status=sponsor_res.match_category.value if sponsor_res else "not_specified",
        remote_compatibility=remote_res.match_category.value if remote_res else "not_specified",
        location_compatibility=loc_res.match_category.value if loc_res else "neutral",
        relocation_compatibility="acceptable",
        compensation_compatibility=f"{int(comp_factor * 100)}%",
        employer_restriction_status="blocked" if is_blocked else "allowed",
        hard_policy_passed=hard_policy_passed,
        hard_policy_reason=hard_policy_reason,
        explanation=summary_exp,
    )

    return JobMatchEvaluation(
        id=generate_uuid(),
        profile_id=applicant_snapshot.profile_id,
        canonical_job_id=canonical_job.get("id", ""),
        job_title=canonical_job.get("title", "Untitled"),
        company_name=canonical_job.get("company", "Employer"),
        job_location=canonical_job.get("location"),
        employment_type=canonical_job.get("employment_type"),
        work_arrangement=canonical_job.get("work_arrangement"),
        career_strategy_id=career_strategy.strategy_id,
        rubric_id=active_rubric.id,
        version=1,
        is_current=True,
        status="completed",
        eligibility_outcome=outcome,
        relevance_index=relevance_index,
        mandatory_coverage_ratio=mandatory_ratio,
        preferred_coverage_ratio=preferred_ratio,
        evidence_completeness_ratio=round(1.0 - uncertainty_ratio, 3),
        ranking_uncertainty_ratio=uncertainty_ratio,
        application_readiness=readiness,
        hard_policy_passed=hard_policy_passed,
        hard_policy_reason=hard_policy_reason,
        summary_explanation=summary_exp,
        requirement_results=atomic_results,
        group_results=group_results,
        skill_details=skill_details,
        education_detail=edu_detail,
        experience_detail=exp_detail,
        eligibility_detail=eligibility_detail,
        score_breakdown=score_breakdown,
        gaps=gaps,
        missing_information=missing_info,
        review_requests=review_requests,
        counterfactuals=counterfactuals,
        evaluated_at=utc_now(),
        updated_at=utc_now(),
    )
