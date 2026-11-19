"""Tests for multi-source job aggregation, exact duplicate rules, and false-merge prevention (Stage 27)."""

import pytest
from uuid import uuid4
from app.db.engine import async_session_factory
from app.recruitment.aggregation.processing.ingestion import observation_ingestion_pipeline
from app.recruitment.aggregation.canonical.registry import canonical_job_registry


@pytest.mark.asyncio
async def test_same_job_multiple_sources():
    """Section 106: Same job discovered across employer career page, Greenhouse, and secondary listing.

    Expected: Merged into 1 canonical job, 3 source links preserved, original URLs preserved,
    source count == 3, search returns 1 canonical job.
    """
    prefix = uuid4().hex[:6]
    async with async_session_factory() as session:
        # Source 1: Employer Careers Page
        job1, merged1 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_career_{prefix}_001",
            source_id="src_career_page",
            provider="career_page",
            native_posting_id=f"STRIPE-REQ-{prefix}",
            title="Senior Infrastructure Engineer",
            employer_name="Stripe",
            source_url=f"https://stripe.com/jobs/{prefix}",
            application_url=f"https://stripe.com/jobs/{prefix}/apply",
            location_raw="San Francisco, CA",
            workplace_type="hybrid",
            employment_type="full_time",
            salary_raw="$180,000 - $220,000",
            description_text=f"Join Stripe infrastructure team to build payment systems. REQ: {prefix}",
        )
        assert merged1 is False
        await session.commit()

        # Source 2: Greenhouse Public Board
        job2, merged2 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_gh_{prefix}_002",
            source_id="src_greenhouse_stripe",
            provider="greenhouse",
            native_posting_id=f"gh_{prefix}",
            title="Senior Infrastructure Engineer",
            employer_name="Stripe Inc.",
            source_url=f"https://boards.greenhouse.io/stripe/jobs/{prefix}",
            application_url=f"https://boards.greenhouse.io/stripe/jobs/{prefix}#app",
            location_raw="San Francisco, CA",
            workplace_type="hybrid",
            employment_type="full_time",
            salary_raw="$180,000 - $220,000",
            description_text=f"Join Stripe infrastructure team to build payment systems. REQ-{prefix}",
        )
        assert merged2 is True
        assert job2.id == job1.id
        await session.commit()

        # Source 3: Secondary Feed
        job3, merged3 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_feed_{prefix}_003",
            source_id="src_tech_feed",
            provider="json_feed",
            native_posting_id=f"feed_stripe_{prefix}",
            title="Senior Infrastructure Engineer",
            employer_name="Stripe",
            source_url=f"https://techjobs.example/stripe/{prefix}",
            application_url=f"https://stripe.com/jobs/{prefix}",
            location_raw="San Francisco, CA",
            workplace_type="hybrid",
            employment_type="full_time",
            salary_raw="$180,000 - $220,000",
            description_text=f"Senior Infrastructure Engineer at Stripe. Requisition: {prefix}",
        )
        assert merged3 is True
        assert job3.id == job1.id
        await session.commit()

        # Verify Canonical Job Record
        loaded = await canonical_job_registry.get_by_id(session, job1.id)
        assert loaded is not None
        assert loaded.source_count == 3
        contract = canonical_job_registry.to_contract(loaded)
        assert len(contract.sources) == 3
        urls = {s.original_url for s in contract.sources}
        assert f"https://stripe.com/jobs/{prefix}" in urls
        assert f"https://boards.greenhouse.io/stripe/jobs/{prefix}" in urls


@pytest.mark.asyncio
async def test_same_title_different_jobs():
    """Section 107: Same employer, same title, but DIFFERENT confirmed requisition IDs!

    Job A: Backend Engineer, Acme Corp, Requisition REQ-1001
    Job B: Backend Engineer, Acme Corp, Requisition REQ-1002
    Expected: MUST remain separate canonical jobs! Fatal contradiction prevents merge.
    """
    prefix = uuid4().hex[:6]
    async with async_session_factory() as session:
        job_a, merged_a = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_acme_req1001_{prefix}",
            source_id="src_acme_careers",
            provider="career_page",
            native_posting_id=f"REQ-1001-{prefix}",
            title="Backend Engineer",
            employer_name="Acme Corp",
            source_url=f"https://acme.com/jobs/req-1001-{prefix}",
            description_text=f"Backend Engineer for the Payments team. REQ: 1001-{prefix}",
        )
        assert merged_a is False
        await session.commit()

        job_b, merged_b = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_acme_req1002_{prefix}",
            source_id="src_acme_careers",
            provider="career_page",
            native_posting_id=f"REQ-1002-{prefix}",
            title="Backend Engineer",
            employer_name="Acme Corp",
            source_url=f"https://acme.com/jobs/req-1002-{prefix}",
            description_text=f"Backend Engineer for the Identity team. REQ: 1002-{prefix}",
        )
        # CRITICAL ASSERTION: Job B must NOT be merged into Job A!
        assert merged_b is False
        assert job_b.id != job_a.id
        await session.commit()

        loaded_a = await canonical_job_registry.get_by_id(session, job_a.id)
        loaded_b = await canonical_job_registry.get_by_id(session, job_b.id)
        assert loaded_a is not None and loaded_b is not None
        assert loaded_a.requisition_id == f"1001-{prefix.upper()}"
        assert loaded_b.requisition_id == f"1002-{prefix.upper()}"


@pytest.mark.asyncio
async def test_different_employers_with_similar_names():
    """Section 108: Alpha Technologies vs Alpha Consulting with similar job titles.

    Expected: Different verified domains keep employers and jobs distinct.
    """
    prefix = uuid4().hex[:6]
    async with async_session_factory() as session:
        job_alpha1, _ = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_alpha_tech_{prefix}",
            source_id="src_alpha_tech",
            provider="career_page",
            native_posting_id=f"job_991_{prefix}",
            title="Cloud Solutions Architect",
            employer_name="Alpha Technologies",
            source_url=f"https://alphatechnologies-{prefix}.com/careers/991",
            description_text="Design cloud architectures for Fortune 500 enterprises.",
        )
        await session.commit()

        job_alpha2, _ = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=f"obs_alpha_consult_{prefix}",
            source_id="src_alpha_consult",
            provider="career_page",
            native_posting_id=f"job_992_{prefix}",
            title="Cloud Solutions Architect",
            employer_name="Alpha Consulting",
            source_url=f"https://alphaconsulting-{prefix}.example/jobs/992",
            description_text="Design cloud architectures for consulting clients.",
        )
        await session.commit()

        assert job_alpha1.id != job_alpha2.id
        assert job_alpha1.employer_id != job_alpha2.employer_id
