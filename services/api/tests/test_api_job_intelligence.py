"""Integration tests for Job Intelligence REST API Endpoints (Stage 28)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.engine import get_db_session
from app.db.models import JobListing, JobSource
from app.main import app
from app.recruitment.intelligence.contracts import (
    AnalysisStatus,
    AtomicRequirement,
    CompensationIntelligence,
    EligibilityConditions,
    EmploymentConditions,
    JobIntelligenceRecord,
    PayPeriod,
    QualificationType,
    RequirementCategory,
    ReviewStatus,
    StructuredSkill,
    WorkplaceType,
)
from app.recruitment.intelligence.service import job_intelligence_service


@pytest.fixture
async def sample_job_in_db():
    import uuid
    uid = str(uuid.uuid4())[:8]
    async with get_db_session() as session:
        # Create JobSource
        source = JobSource(
            id=f"src-test-{uid}",
            platform_name="Greenhouse",
            source_type="api",
            source_url=f"https://api.greenhouse.io/{uid}",
            enabled=True,
        )
        session.add(source)
        await session.flush()

        # Create JobListing
        listing = JobListing(
            id=f"job-intel-test-{uid}",
            source_id=f"src-test-{uid}",
            external_id=f"gh-{uid}",
            company="Stripe",
            title="Senior Staff Infrastructure Engineer",
            location="Remote",
            work_arrangement="remote",
            salary_range="$190,000 - $240,000 / year",
            description="""
            About Stripe:
            We build economic infrastructure for the internet.

            Responsibilities:
            * Architect distributed databases in Go and Python.
            * Scale infrastructure reliability.

            Minimum Qualifications:
            * Bachelor's degree in Computer Science or equivalent practical experience.
            * 6+ years of software engineering experience.
            * Strong experience with Docker and Kubernetes.
            * Must have valid US work authorization.

            Preferred Qualifications:
            * Experience with Terraform and AWS.

            Compensation:
            Salary range: $190,000 - $240,000 annually.
            Eligible for equity and annual bonus.
            Benefits: 401(k) matching and healthcare.

            How to Apply:
            Applications close on Deadline: June 15, 2026. Submit Resume and Cover Letter.
            """,
            application_url="https://stripe.com/jobs/12345",
            status="active",
        )
        session.add(listing)
        await session.commit()
    return listing.id


@pytest.mark.asyncio
async def test_api_intelligence_status_and_diagnostics(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/job-intelligence/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_records" in data
        assert "extractor_version" in data
        assert data["extractor_version"] == "1.0.0"

        diag = await client.get("/api/v1/job-intelligence/diagnostics", headers=auth_headers)
        assert diag.status_code == 200


@pytest.mark.asyncio
async def test_api_analyze_and_fetch_job(auth_headers, sample_job_in_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        job_id = sample_job_in_db

        # 1. Trigger analysis
        analyze_res = await client.post(
            f"/api/v1/job-intelligence/jobs/{job_id}/analyze",
            json={"force": True, "use_ai": False},
            headers=auth_headers,
        )
        assert analyze_res.status_code == 200
        rec = analyze_res.json()
        assert rec["canonical_job_id"] == job_id
        assert rec["analysis_status"] in ("Completed", "NeedsReview")
        assert len(rec["mandatory_requirements"]) >= 2

        # 2. Get record
        get_res = await client.get(f"/api/v1/job-intelligence/jobs/{job_id}", headers=auth_headers)
        assert get_res.status_code == 200
        assert get_res.json()["canonical_job_id"] == job_id

        # 3. Get skills
        skills_res = await client.get(f"/api/v1/job-intelligence/jobs/{job_id}/skills", headers=auth_headers)
        assert skills_res.status_code == 200
        skills = skills_res.json()
        skill_names = [s["name"] for s in skills]
        assert "Docker" in skill_names
        assert "Kubernetes" in skill_names

        # 4. Get education
        edu_res = await client.get(f"/api/v1/job-intelligence/jobs/{job_id}/education", headers=auth_headers)
        assert edu_res.status_code == 200
        edu = edu_res.json()
        assert len(edu) >= 1
        assert edu[0]["degree_level"] == "BACHELOR"

        # 5. Get compensation
        comp_res = await client.get(f"/api/v1/job-intelligence/jobs/{job_id}/compensation", headers=auth_headers)
        assert comp_res.status_code == 200
        comp = comp_res.json()
        assert comp["is_disclosed"] is True
        assert comp["base_min"] == 190000.0
        assert comp["base_max"] == 240000.0

        # 6. Get deadlines
        dl_res = await client.get(f"/api/v1/job-intelligence/jobs/{job_id}/deadlines", headers=auth_headers)
        assert dl_res.status_code == 200
        dl = dl_res.json()
        assert dl["deadline_utc"] is not None


@pytest.mark.asyncio
async def test_api_review_queue_and_resolve(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create an in-memory record needing review
        record = JobIntelligenceRecord(
            id="intel-review-test-1",
            canonical_job_id="job-rev-1",
            description_hash="hashrev",
            job_title="Security Lead",
            analysis_status=AnalysisStatus.NEEDS_REVIEW,
            review_status=ReviewStatus.PENDING,
        )
        job_intelligence_service._in_memory_records["job-rev-1"] = record

        # Get review queue
        resp = await client.get("/api/v1/job-intelligence/review-queue", headers=auth_headers)
        assert resp.status_code == 200
