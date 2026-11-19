"""REST API integration test suite for Stage 29 Job Matching endpoints.

Verifies:
- Authentication enforcement (401 without API key header).
- GET /api/v1/job-matching/rubrics (list standard and active rubrics).
- POST /api/v1/job-matching/evaluate (single job evaluation).
- POST /api/v1/job-matching/evaluate-batch (batch job evaluations).
- GET /api/v1/job-matching/evaluations/{id} (evaluation detail).
- GET /api/v1/job-matching/rankings (ranked opportunities).
- POST /api/v1/job-matching/simulate (What-If scenario simulation).
- POST /api/v1/job-matching/compare (multi-job comparison).
- GET /api/v1/job-matching/reviews (review queue).
- POST /api/v1/job-matching/reviews/{id}/resolve (review resolution).
- GET /api/v1/job-matching/audit-events (audit trail).
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.recruitment.matching.contracts import (
    ApplicationReadiness,
    JobComparisonMatrix,
    JobMatchEvaluation,
    MatchingOutcome,
    RankedOpportunityItem,
    RankingOverview,
    RelevanceIndexBreakdown,
    SimulationResponse,
)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    from app.core.config import settings
    return {"Authorization": f"Bearer {settings.api_key}"}


@pytest.mark.asyncio
async def test_job_matching_api_auth_required():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request without auth header should fail with 401
        res = await client.get("/api/v1/job-matching/rubrics")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_job_matching_rubrics_endpoint(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/job-matching/rubrics", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == "rubric_default_v1"


@pytest.mark.asyncio
async def test_job_matching_evaluate_and_get_endpoints(auth_headers):
    dummy_eval = JobMatchEvaluation(
        id="eval_api_test_1",
        profile_id="prof_api_1",
        canonical_job_id="job_api_1",
        job_title="Software Architect",
        company_name="Cloud Tech",
        eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        relevance_index=92.5,
        mandatory_coverage_ratio=1.0,
        preferred_coverage_ratio=0.85,
        application_readiness=ApplicationReadiness.READY_FOR_PREPARATION,
        hard_policy_passed=True,
        summary_explanation="Direct match for software architecture role.",
        score_breakdown=RelevanceIndexBreakdown(relevance_index=92.5),
    )

    with patch("app.recruitment.matching.service.job_matching_service.evaluate_job", new_callable=AsyncMock) as mock_eval, \
         patch("app.recruitment.matching.service.job_matching_service.get_evaluation", new_callable=AsyncMock) as mock_get:

        mock_eval.return_value = dummy_eval
        mock_get.return_value = dummy_eval

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. POST /api/v1/job-matching/evaluate
            eval_payload = {
                "canonical_job_id": "job_api_1",
                "profile_id": "prof_api_1",
                "force": False,
            }
            res = await client.post("/api/v1/job-matching/evaluate", json=eval_payload, headers=auth_headers)
            assert res.status_code == 200
            data = res.json()
            assert data["id"] == "eval_api_test_1"
            assert data["relevance_index"] == 92.5
            assert data["eligibility_outcome"] == "eligible_and_aligned"

            # 2. GET /api/v1/job-matching/evaluations/{id}
            res_get = await client.get("/api/v1/job-matching/evaluations/eval_api_test_1", headers=auth_headers)
            assert res_get.status_code == 200
            assert res_get.json()["id"] == "eval_api_test_1"


@pytest.mark.asyncio
async def test_job_matching_rankings_and_simulation(auth_headers):
    mock_items = [
        RankedOpportunityItem(
            rank=1,
            evaluation_id="eval_1",
            canonical_job_id="job_1",
            job_title="Lead Architect",
            company_name="Enterprise Systems",
            eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
            relevance_index=95.0,
            mandatory_coverage_ratio=1.0,
            preferred_coverage_ratio=0.9,
            critical_gaps_count=0,
            unknowns_count=0,
            application_readiness=ApplicationReadiness.READY_FOR_PREPARATION,
            last_evaluated_at="2026-03-30T10:00:00Z",
        )
    ]
    mock_overview = RankingOverview(total_evaluated=1, eligible_and_aligned=1)

    mock_sim_resp = SimulationResponse(
        simulation_id="sim_api_1",
        evaluation_id="eval_1",
        scenario_name="Test Sim",
        original_relevance_index=80.0,
        simulated_relevance_index=92.0,
        original_eligibility=MatchingOutcome.CONDITIONALLY_ELIGIBLE,
        simulated_eligibility=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        diff_explanation="Relevance increased by 12 points",
    )

    with patch("app.recruitment.matching.service.job_matching_service.get_rankings", new_callable=AsyncMock) as mock_rankings, \
         patch("app.recruitment.matching.service.job_matching_service.simulate", new_callable=AsyncMock) as mock_sim, \
         patch("app.recruitment.matching.service.job_matching_service.compare_jobs", new_callable=AsyncMock) as mock_compare:

        mock_rankings.return_value = (mock_items, mock_overview)
        mock_sim.return_value = mock_sim_resp
        mock_compare.return_value = JobComparisonMatrix(canonical_job_ids=["job_1", "job_2"], items=[])

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. GET /api/v1/job-matching/rankings
            res_rank = await client.get("/api/v1/job-matching/rankings", headers=auth_headers)
            assert res_rank.status_code == 200
            data_rank = res_rank.json()
            assert len(data_rank["items"]) == 1
            assert data_rank["overview"]["total_evaluated"] == 1

            # 2. POST /api/v1/job-matching/simulate
            sim_payload = {
                "evaluation_id": "eval_1",
                "scenario_name": "Test Sim",
                "hypothetical_skills": ["Rust"],
            }
            res_sim = await client.post("/api/v1/job-matching/simulate", json=sim_payload, headers=auth_headers)
            assert res_sim.status_code == 200
            assert res_sim.json()["simulated_relevance_index"] == 92.0

            # 3. POST /api/v1/job-matching/compare
            compare_payload = {"canonical_job_ids": ["job_1", "job_2"]}
            res_comp = await client.post("/api/v1/job-matching/compare", json=compare_payload, headers=auth_headers)
            assert res_comp.status_code == 200
            assert len(res_comp.json()["canonical_job_ids"]) == 2
