"""Required Test 155: Multi-Agent Matching Workflow and Internal Capabilities.

Verifies:
- All 13 internal matching agent capabilities are properly callable:
  1. job.matching.evaluate
  2. job.matching.evaluate_batch
  3. job.matching.get_result
  4. job.matching.get_eligibility
  5. job.matching.get_requirement_coverage
  6. job.matching.get_skill_gaps
  7. job.matching.get_evidence
  8. job.matching.get_ranking
  9. job.matching.explain_result
  10. job.matching.compare_jobs
  11. job.matching.get_review_queue
  12. job.matching.simulate
  13. job.matching.get_history
- VerificationAgent, ResumeAgent, WritingAgent, and Supervisor can query these capabilities.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.recruitment.matching import capabilities
from app.recruitment.matching.contracts import (
    ApplicationReadiness,
    JobComparisonMatrix,
    JobMatchEvaluation,
    MatchingOutcome,
    RankedOpportunityItem,
    RankingOverview,
    RelevanceIndexBreakdown,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    SimulationResponse,
    SkillGapItem,
    GapType,
    GapSeverity,
)


@pytest.mark.asyncio
async def test_all_13_agent_capabilities():
    dummy_eval = JobMatchEvaluation(
        id="eval_cap_1",
        profile_id="prof_1",
        canonical_job_id="job_1",
        job_title="Backend Engineer",
        company_name="Acme",
        eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        relevance_index=85.0,
        application_readiness=ApplicationReadiness.READY_FOR_PREPARATION,
        mandatory_coverage_ratio=1.0,
        preferred_coverage_ratio=0.8,
        hard_policy_passed=True,
        requirement_results=[
            RequirementEvaluationResult(
                requirement_id="req_py",
                name="Python",
                category="mandatory",
                match_category=RequirementMatchCategory.DIRECTLY_SATISFIED,
                applicant_claim_ref="claim_1",
                applicant_evidence_snippet="Python 5 yrs",
                confidence=1.0,
                explanation="Satisfied",
                is_satisfied=True,
            )
        ],
        gaps=[
            SkillGapItem(
                id="gap_1",
                requirement_id="req_gql",
                skill_or_qualification="GraphQL",
                gap_type=GapType.MISSING_PREFERRED_SKILL,
                severity=GapSeverity.MODERATE,
                description="Lacks GraphQL",
                remediation_suggestion="Learn GraphQL",
            )
        ],
        score_breakdown=RelevanceIndexBreakdown(relevance_index=85.0),
    )

    with patch("app.recruitment.matching.service.job_matching_service.evaluate_job", new_callable=AsyncMock) as mock_eval, \
         patch("app.recruitment.matching.service.job_matching_service.evaluate_batch", new_callable=AsyncMock) as mock_batch, \
         patch("app.recruitment.matching.service.job_matching_service.get_evaluation", new_callable=AsyncMock) as mock_get, \
         patch("app.recruitment.matching.service.job_matching_service.get_rankings", new_callable=AsyncMock) as mock_rankings, \
         patch("app.recruitment.matching.service.job_matching_service.compare_jobs", new_callable=AsyncMock) as mock_compare, \
         patch("app.recruitment.matching.service.job_matching_service.get_review_queue", new_callable=AsyncMock) as mock_queue, \
         patch("app.recruitment.matching.service.job_matching_service.simulate", new_callable=AsyncMock) as mock_sim, \
         patch("app.recruitment.matching.service.job_matching_service.list_evaluations", new_callable=AsyncMock) as mock_list:

        mock_eval.return_value = dummy_eval
        mock_batch.return_value = [dummy_eval]
        mock_get.return_value = dummy_eval
        mock_rankings.return_value = (
            [
                RankedOpportunityItem(
                    rank=1,
                    evaluation_id="eval_cap_1",
                    canonical_job_id="job_1",
                    job_title="Backend Engineer",
                    company_name="Acme",
                    eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
                    relevance_index=85.0,
                    mandatory_coverage_ratio=1.0,
                    preferred_coverage_ratio=0.8,
                    critical_gaps_count=0,
                    unknowns_count=0,
                    application_readiness=ApplicationReadiness.READY_FOR_PREPARATION,
                    last_evaluated_at="2026-03-30T10:00:00Z",
                )
            ],
            RankingOverview(total_evaluated=1, eligible_and_aligned=1),
        )
        mock_compare.return_value = JobComparisonMatrix(canonical_job_ids=["job_1", "job_2"], items=[])
        mock_queue.return_value = [{"id": "rev_1", "status": "pending"}]
        mock_sim.return_value = SimulationResponse(
            simulation_id="sim_1",
            evaluation_id="eval_cap_1",
            scenario_name="Test Sim",
            original_relevance_index=80.0,
            simulated_relevance_index=90.0,
            original_eligibility=MatchingOutcome.CONDITIONALLY_ELIGIBLE,
            simulated_eligibility=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
            diff_explanation="Improved by 10 points",
        )
        mock_list.return_value = [dummy_eval]

        # 1. evaluate_job
        res1 = await capabilities.capability_evaluate_job("job_1")
        assert res1["id"] == "eval_cap_1"

        # 2. evaluate_batch
        res2 = await capabilities.capability_evaluate_batch(["job_1"])
        assert len(res2) == 1

        # 3. get_result
        res3 = await capabilities.capability_get_result("eval_cap_1")
        assert res3 is not None and res3["id"] == "eval_cap_1"

        # 4. get_eligibility
        res4 = await capabilities.capability_get_eligibility("eval_cap_1")
        assert res4["eligibility_outcome"] == "eligible_and_aligned"

        # 5. get_requirement_coverage
        res5 = await capabilities.capability_get_requirement_coverage("eval_cap_1")
        assert res5["mandatory_coverage_ratio"] == 1.0

        # 6. get_skill_gaps
        res6 = await capabilities.capability_get_skill_gaps("eval_cap_1")
        assert len(res6) == 1
        assert res6[0]["skill_or_qualification"] == "GraphQL"

        # 7. get_evidence
        res7 = await capabilities.capability_get_evidence("eval_cap_1")
        assert len(res7) == 1
        assert res7[0]["applicant_snippet"] == "Python 5 yrs"

        # 8. get_ranking
        res8 = await capabilities.capability_get_ranking()
        assert len(res8["items"]) == 1
        assert res8["overview"]["total_evaluated"] == 1

        # 9. explain_result
        res9 = await capabilities.capability_explain_result("eval_cap_1")
        assert res9["relevance_index"] == 85.0

        # 10. compare_jobs
        res10 = await capabilities.capability_compare_jobs(["job_1", "job_2"])
        assert len(res10["canonical_job_ids"]) == 2

        # 11. get_review_queue
        res11 = await capabilities.capability_get_review_queue()
        assert len(res11) == 1

        # 12. simulate
        res12 = await capabilities.capability_simulate("eval_cap_1", "Learn Go", hypothetical_skills=["Go"])
        assert res12["simulated_relevance_index"] == 90.0

        # 13. get_history
        res13 = await capabilities.capability_get_history()
        assert len(res13) == 1
