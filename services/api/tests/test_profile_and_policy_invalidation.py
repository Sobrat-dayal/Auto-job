"""Required Tests 148, 149, 150: Evaluation Lifecycle and Invalidation.

Verifies:
- Test 148: Applicant profile version update invalidates cache and marks prior evaluations not current.
- Test 149: Canonical job version update invalidates prior match evaluations.
- Test 150: Career Strategy update invalidates all matching evaluations associated with that strategy.
- Cache key computation via SHA-256 changes whenever profile version, job version, or rubric version increments.
"""

import pytest
from app.db.engine import get_db_session
from app.db.models import JobMatchEvaluationModel
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    RubricConfig,
)
from app.recruitment.matching.lifecycle.caching import (
    clear_cache,
    generate_cache_key,
    get_cached_evaluation,
    set_cached_evaluation,
)
from app.recruitment.matching.lifecycle.invalidation import (
    invalidate_for_job_update,
    invalidate_for_policy_update,
    invalidate_for_profile_update,
)


def test_cache_key_generation_deterministic():
    app_v1 = ApplicantSnapshotData(
        profile_id="prof_inv_1", version=1, headline="Dev", country="US", city="NY",
        authorized_countries=["US"], requires_sponsorship=False,
        skills=[], education=[], experience=[], projects=[], certifications=[],
    )
    app_v2 = ApplicantSnapshotData(
        profile_id="prof_inv_1", version=2, headline="Dev", country="US", city="NY",
        authorized_countries=["US"], requires_sponsorship=False,
        skills=[], education=[], experience=[], projects=[], certifications=[],
    )
    job_v1 = JobIntelligenceSnapshotData(
        canonical_job_id="job_inv_1", canonical_job_version=1,
        job_title="Dev", company_name="Corp",
    )
    job_v2 = JobIntelligenceSnapshotData(
        canonical_job_id="job_inv_1", canonical_job_version=2,
        job_title="Dev", company_name="Corp",
    )
    policy_v1 = CareerStrategySnapshotData(
        strategy_id="strat_inv_1", title="Strat",
    )
    rubric_v1 = RubricConfig(id="rubric_v1", version=1)
    rubric_v2 = RubricConfig(id="rubric_v1", version=2)

    # 1. Deterministic repeatability
    key_a1 = generate_cache_key(app_v1, job_v1, policy_v1, rubric_v1)
    key_a2 = generate_cache_key(app_v1, job_v1, policy_v1, rubric_v1)
    assert key_a1 == key_a2

    # 2. Key changes on applicant version bump (Test 148)
    key_app_v2 = generate_cache_key(app_v2, job_v1, policy_v1, rubric_v1)
    assert key_a1 != key_app_v2

    # 3. Key changes on job version bump (Test 149)
    key_job_v2 = generate_cache_key(app_v1, job_v2, policy_v1, rubric_v1)
    assert key_a1 != key_job_v2

    # 4. Key changes on rubric version bump
    key_rub_v2 = generate_cache_key(app_v1, job_v1, policy_v1, rubric_v2)
    assert key_a1 != key_rub_v2


@pytest.mark.asyncio
async def test_database_invalidation_lifecycle():
    from app.db.models import ApplicantProfile, JobSource, JobListing

    async with get_db_session() as session:
        # Create prerequisite models
        profile = ApplicantProfile(
            id="prof_db_inv_1",
            profile_name="Test Invalidation Profile",
            summary="Bio",
        )
        source = JobSource(
            id="src_db_inv_1",
            platform_name="greenhouse",
            source_type="api",
            source_url="https://boards-api.greenhouse.io/v1/boards/inv_test/jobs",
        )
        job = JobListing(
            id="job_db_inv_1",
            source_id="src_db_inv_1",
            external_id="ext_inv_1",
            company="Test Corp",
            title="Senior Developer",
            application_url="https://example.com/jobs/inv-1",
        )
        session.add(profile)
        session.add(source)
        session.add(job)
        await session.commit()

        # Insert test evaluation in SQLite
        eval1 = JobMatchEvaluationModel(
            id="eval_inv_test_1",
            profile_id="prof_db_inv_1",
            canonical_job_id="job_db_inv_1",
            career_strategy_id="strat_db_inv_1",
            version=1,
            is_current=True,
            status="completed",
            eligibility_outcome="eligible_and_aligned",
            relevance_index=88.0,
            mandatory_coverage_ratio=1.0,
            preferred_coverage_ratio=0.8,
            evidence_completeness_ratio=1.0,
            ranking_uncertainty_ratio=0.0,
            application_readiness="ready_for_preparation",
            hard_policy_passed=True,
            summary_explanation="Test eval 1",
            score_components_json={},
            input_snapshots_json={},
            gaps_summary_json=[],
            recommendation_tags_json=[],
        )
        session.add(eval1)
        await session.commit()

        # 1. Test 148: Invalidation for profile update
        count = await invalidate_for_profile_update("prof_db_inv_1", session)
        await session.commit()
        assert count >= 1

        refreshed = await session.get(JobMatchEvaluationModel, "eval_inv_test_1")
        assert refreshed is not None
        assert refreshed.is_current is False

        # Reset is_current for Test 149
        refreshed.is_current = True
        await session.commit()

        # 2. Test 149: Invalidation for job update
        count_job = await invalidate_for_job_update("job_db_inv_1", session)
        await session.commit()
        assert count_job >= 1

        refreshed_job = await session.get(JobMatchEvaluationModel, "eval_inv_test_1")
        assert refreshed_job is not None
        assert refreshed_job.is_current is False

        # Reset is_current for Test 150
        refreshed_job.is_current = True
        await session.commit()

        # 3. Test 150: Invalidation for policy update
        count_policy = await invalidate_for_policy_update("strat_db_inv_1", session)
        await session.commit()
        assert count_policy >= 1

        refreshed_policy = await session.get(JobMatchEvaluationModel, "eval_inv_test_1")
        assert refreshed_policy is not None
        assert refreshed_policy.is_current is False

        # Clean up
        await session.delete(refreshed_policy)
        await session.delete(job)
        await session.delete(source)
        await session.delete(profile)
        await session.commit()
