"""Tests for employer identity resolution, aliases, domains, and ATS boards (Stage 27)."""

import pytest
from uuid import uuid4
from app.db.engine import async_session_factory
from app.recruitment.aggregation.contracts import OrganizationType
from app.recruitment.aggregation.employers.identity import employer_identity_resolver
from app.recruitment.aggregation.employers.registry import employer_registry
from app.recruitment.aggregation.employers.relationships import classify_organization_type
from app.recruitment.aggregation.integrations.career_policy import career_policy_integration


@pytest.mark.asyncio
async def test_employer_alias_resolution():
    """Section 109: Resolve legal name, trading name, and abbreviations to one canonical employer."""
    prefix = uuid4().hex[:6]
    corp_name = f"International Business Machines {prefix}"

    async with async_session_factory() as session:
        # Create canonical employer with domain & alias
        emp = await employer_registry.create_employer(
            session=session,
            name=corp_name,
            legal_name=f"{corp_name} Corporation",
            official_careers_url=f"https://www.ibm-{prefix}.com/careers",
            primary_domain=f"ibm-{prefix}.com",
        )
        await session.commit()

        # Ingest with legal name variation
        res1, ev1 = await employer_identity_resolver.resolve_employer(
            session=session,
            raw_name=f"{corp_name} Corp.",
            source_url=f"https://www.ibm-{prefix}.com/jobs/1",
            provider="career_page",
        )
        assert res1.id == emp.id

        # Ingest with board link
        res2, ev2 = await employer_identity_resolver.resolve_employer(
            session=session,
            raw_name=corp_name,
            source_url=f"https://boards.greenhouse.io/{prefix}-ibm/jobs/2",
            provider="greenhouse",
        )
        assert res2.id == emp.id


@pytest.mark.asyncio
async def test_staffing_agency_classification():
    """Section 16: Ensure recruiting intermediaries and staffing agencies are classified accurately."""
    org1 = classify_organization_type("Robert Half Technology")
    assert org1 == OrganizationType.STAFFING_AGENCY

    org2 = classify_organization_type("TEKsystems Global Services")
    assert org2 == OrganizationType.STAFFING_AGENCY

    org3 = classify_organization_type("Apple Computer Inc.")
    assert org3 == OrganizationType.DIRECT_EMPLOYER

    org4 = classify_organization_type("Acme Corp", description="Position offered on behalf of our client.")
    assert org4 == OrganizationType.STAFFING_AGENCY


@pytest.mark.asyncio
async def test_career_policy_blocked_employer():
    """Section 118: Ensure blocked employer is rejected by career policy."""
    async with async_session_factory() as session:
        is_blocked, reason = await career_policy_integration.is_employer_blocked(
            session=session,
            employer_id="emp_evil_001",
            employer_name="Evil Corp",
        )
        assert is_blocked is True
        assert "blocklist" in reason.lower()

        is_blocked_ok, _ = await career_policy_integration.is_employer_blocked(
            session=session,
            employer_id="emp_good_001",
            employer_name="Good Tech Labs",
        )
        assert is_blocked_ok is False
