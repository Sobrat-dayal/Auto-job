"""Tests for field conflict detection, source authority, and resolution (Stage 27)."""

import pytest
from uuid import uuid4
from app.db.engine import async_session_factory
from app.recruitment.aggregation.canonical.conflicts import field_conflict_manager
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.processing.ingestion import observation_ingestion_pipeline
from app.recruitment.aggregation.reconciliation.source_authority import get_source_authority_score


@pytest.mark.asyncio
async def test_field_conflict_detection_and_resolution():
    """Section 113: Multi-source field conflicts detected, preserved, and resolvable."""
    prefix = uuid4().hex[:6]
    req_id = f"CONF-{prefix}"

    async with async_session_factory() as session:
        # Source A: Remote, salary $150k-$170k
        job1, _ = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_src_a_{prefix}",
            source_id="src_official_career",
            provider="career_page",
            native_posting_id=f"post_{prefix}",
            title="Senior DevOps Engineer",
            employer_name="Conflict Labs",
            source_url=f"https://conflictlabs.example/jobs/{prefix}",
            location_raw="Remote, US",
            workplace_type="remote",
            salary_raw="$150,000 - $170,000",
            description_text=f"DevOps position. REQ: {req_id}",
        )
        await session.commit()

        # Source B: Hybrid, salary $160k-$190k
        job2, merged = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_src_b_{prefix}",
            source_id="src_secondary_board",
            provider="greenhouse",
            native_posting_id=f"post_{prefix}",
            title="Senior DevOps Engineer",
            employer_name="Conflict Labs",
            source_url=f"https://boards.greenhouse.io/conflictlabs/jobs/{prefix}",
            location_raw="Austin, TX",
            workplace_type="hybrid",
            salary_raw="$160,000 - $190,000",
            description_text=f"DevOps position. REQ: {req_id}",
        )
        assert merged is True
        await session.commit()

        # Verify conflicts logged
        loaded = await canonical_job_registry.get_by_id(session, job1.id)
        assert loaded.conflict_state == "has_conflicts"
        conflicts = loaded.conflicts
        assert len(conflicts) >= 1

        # Check salary mismatch logged
        sal_conf = next((c for c in conflicts if c.field_name == "compensation_summary"), None)
        assert sal_conf is not None
        assert sal_conf.status == "unresolved"
        assert "$150,000 - $170,000" in str(sal_conf.source_values_json)
        assert "$160,000 - $190,000" in str(sal_conf.source_values_json)

        # Resolve conflict manually
        res = await field_conflict_manager.resolve_conflict(
            session=session,
            conflict_id=sal_conf.id,
            chosen_value="$150,000 - $170,000 (Official career site)",
            resolution_note="Preferred official employer career site over aggregator",
            resolved_by="user_alice",
        )
        assert res is not None
        assert res.status == "resolved_by_user"
        assert res.resolved_by == "user_alice"
        await session.commit()


def test_source_authority_scoring():
    """Section 47: Verify source authority rules give priority to official career portals."""
    auth_career = get_source_authority_score("career_page")
    auth_api = get_source_authority_score("official_public_api")
    auth_gh = get_source_authority_score("greenhouse")
    auth_feed = get_source_authority_score("rss_atom_feed")
    auth_manual = get_source_authority_score("manual_import")

    assert auth_career >= auth_api
    assert auth_api >= auth_gh
    assert auth_gh > auth_feed
    assert auth_feed > auth_manual
