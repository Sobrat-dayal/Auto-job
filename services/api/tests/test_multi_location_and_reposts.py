"""Tests for multi-location postings, evergreen handling, and repost detection (Stage 27)."""

import pytest
from uuid import uuid4
from app.db.engine import async_session_factory
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.processing.ingestion import observation_ingestion_pipeline


@pytest.mark.asyncio
async def test_multi_location_same_requisition():
    """Section 110 Case A: One confirmed requisition advertised across multiple locations."""
    prefix = uuid4().hex[:6]
    req_id = f"MULTI-{prefix}"

    async with async_session_factory() as session:
        # First observation: New York office
        job1, merged1 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_loc_ny_{prefix}",
            source_id="src_multi_loc",
            provider="greenhouse",
            native_posting_id=f"req_{prefix}_ny",
            title="Senior Systems Engineer",
            employer_name="MultiLoc Corp",
            source_url=f"https://multiloc.example/jobs/{prefix}?loc=ny",
            location_raw="New York, NY",
            workplace_type="onsite",
            description_text=f"Senior Systems Engineer in NYC. REQ: {req_id}",
        )
        assert merged1 is False
        await session.commit()

        # Second observation: London office with same REQ ID
        job2, merged2 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_loc_lon_{prefix}",
            source_id="src_multi_loc",
            provider="greenhouse",
            native_posting_id=f"req_{prefix}_lon",
            title="Senior Systems Engineer",
            employer_name="MultiLoc Corp",
            source_url=f"https://multiloc.example/jobs/{prefix}?loc=lon",
            location_raw="London, UK",
            workplace_type="onsite",
            description_text=f"Senior Systems Engineer in London. REQ: {req_id}",
        )
        assert merged2 is True
        assert job2.id == job1.id
        await session.commit()

        loaded = await canonical_job_registry.get_by_id(session, job1.id)
        assert loaded.source_count == 2


@pytest.mark.asyncio
async def test_reposted_vacancy_preservation():
    """Section 111: Vacancy reappears after closure with a different requisition ID."""
    prefix = uuid4().hex[:6]

    async with async_session_factory() as session:
        # Original vacancy in Q1
        job_old, _ = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_old_q1_{prefix}",
            source_id="src_repost_test",
            provider="career_page",
            native_posting_id=f"Q1-REQ-{prefix}",
            title="Staff Site Reliability Engineer",
            employer_name="Cloudscale Inc",
            source_url=f"https://cloudscale.example/jobs/q1-{prefix}",
            description_text=f"Staff SRE for Cloudscale. REQ: Q1-{prefix}",
        )
        # Mark closed
        job_old.status = "closed"
        await session.commit()

        # Later vacancy in Q3 with new requisition ID
        job_new, merged = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_new_q3_{prefix}",
            source_id="src_repost_test",
            provider="career_page",
            native_posting_id=f"Q3-REQ-{prefix}",
            title="Staff Site Reliability Engineer",
            employer_name="Cloudscale Inc",
            source_url=f"https://cloudscale.example/jobs/q3-{prefix}",
            description_text=f"Staff SRE for Cloudscale. REQ: Q3-{prefix}",
        )
        # MUST NOT blindly merge into closed vacancy because of distinct requisition ID
        assert merged is False
        assert job_new.id != job_old.id


@pytest.mark.asyncio
async def test_evergreen_posting_refresh():
    """Section 112: Evergreen talent pool periodically fetched without creating duplicate canonical jobs."""
    prefix = uuid4().hex[:6]

    async with async_session_factory() as session:
        # First discovery
        job1, m1 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_evergreen_{prefix}",
            source_id="src_evergreen",
            provider="lever",
            native_posting_id=f"evergreen_{prefix}",
            title="General Engineering Application",
            employer_name="Evergreen Labs",
            source_url=f"https://jobs.lever.co/evergreen/general-{prefix}",
            description_text=f"Open rolling application for engineers. REQ: EVG-{prefix}",
        )
        assert m1 is False
        job1.is_evergreen = True
        await session.commit()

        # Re-fetch identical observation during next discovery run
        job2, m2 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_evergreen_{prefix}",
            source_id="src_evergreen",
            provider="lever",
            native_posting_id=f"evergreen_{prefix}",
            title="General Engineering Application",
            employer_name="Evergreen Labs",
            source_url=f"https://jobs.lever.co/evergreen/general-{prefix}",
            description_text=f"Open rolling application for engineers. REQ: EVG-{prefix}",
        )
        assert job2.id == job1.id
        # Idempotent re-fetch returns existing job without duplication
        loaded = await canonical_job_registry.get_by_id(session, job1.id)
        assert loaded.version == 1
