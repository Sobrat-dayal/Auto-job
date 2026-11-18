"""Integration tests for Stage 23 Resume Intelligence & Portfolio REST endpoints."""

import pytest
from httpx import AsyncClient

from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ContactInfo,
    EducationRecord,
    EmploymentRecord,
    AchievementItem,
    SkillItem,
    SkillCategory,
    ProficiencyLevel,
)
from app.recruitment.profile.service import applicant_profile_service


@pytest.fixture(autouse=True)
def seed_profile():
    """Ensure applicant profile exists for resume synthesis."""
    profile = ApplicantProfile(
        id="prof_primary_applicant",
        owner_id="default_user",
        contact=ContactInfo(
            legal_name="Sarah Connor",
            primary_email="sarah.connor@example.com",
            phone="+1-555-0177",
            portfolio_url="https://github.com/sarahconnor",
        ),
        education=[
            EducationRecord(
                id="edu_01",
                institution="Caltech",
                degree="B.S.",
                field_of_study="Computer Science",
                start_date="2016-09-01",
                end_date="2020-06-01",
            )
        ],
        experience=[
            EmploymentRecord(
                id="exp_01",
                employer="Cyberdyne Systems",
                job_title="Systems Engineer",
                start_date="2020-07-01",
                end_date=None,
                is_current=True,
                achievements=[
                    AchievementItem(
                        id="ach_01",
                        statement="Developed fault-tolerant distributed automation control nodes",
                    )
                ],
                technologies=["Python", "FastAPI", "Linux"],
            )
        ],
        skills=[
            SkillItem(id="sk_01", name="Python", canonical_name="python", category=SkillCategory.PROGRAMMING_LANGUAGES, proficiency=ProficiencyLevel.EXPERT),
            SkillItem(id="sk_02", name="FastAPI", canonical_name="fastapi", category=SkillCategory.BACKEND, proficiency=ProficiencyLevel.ADVANCED),
            SkillItem(id="sk_03", name="Linux", canonical_name="linux", category=SkillCategory.CLOUD_DEVOPS, proficiency=ProficiencyLevel.ADVANCED),
        ],
    )
    applicant_profile_service._profiles["prof_primary_applicant"] = profile
    return profile


@pytest.mark.asyncio
async def test_resumes_overview_and_templates(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Overview
    res = await async_client.get("/api/v1/resumes/overview", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_resumes" in data
    assert "draft_count" in data

    # 2. Templates
    tpl_res = await async_client.get("/api/v1/resume-templates", headers=auth_headers)
    assert tpl_res.status_code == 200
    templates = tpl_res.json()
    assert len(templates) >= 6
    tpl_ids = [t["id"] for t in templates]
    assert "ats_classic" in tpl_ids
    assert "modern_professional" in tpl_ids
    assert "technical_engineer" in tpl_ids


@pytest.mark.asyncio
async def test_resume_crud_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create Resume
    create_payload = {
        "title": "Systems Engineer Resume 2026",
        "resume_type": "experienced",
        "target_role": "Systems Engineer",
        "template_id": "ats_classic",
        "page_format": "letter",
        "max_pages": 1,
    }
    create_res = await async_client.post("/api/v1/resumes", json=create_payload, headers=auth_headers)
    assert create_res.status_code in (200, 201)
    resume = create_res.json()
    resume_id = resume["id"]
    assert resume["title"] == "Systems Engineer Resume 2026"
    assert len(resume["sections"]) > 0

    # 2. Get Resume
    get_res = await async_client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == resume_id

    # 3. Update Resume
    patch_payload = {
        "title": "Senior Systems Engineer Resume",
        "target_role": "Senior Systems Engineer",
    }
    patch_res = await async_client.patch(f"/api/v1/resumes/{resume_id}", json=patch_payload, headers=auth_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Senior Systems Engineer Resume"

    # 4. ATS Report
    ats_res = await async_client.get(f"/api/v1/resumes/{resume_id}/ats-report", headers=auth_headers)
    assert ats_res.status_code == 200
    ats_data = ats_res.json()
    assert "overall_status" in ats_data
    assert "checks" in ats_data

    # 5. Preview HTML
    prev_res = await async_client.get(f"/api/v1/resumes/{resume_id}/preview", headers=auth_headers)
    assert prev_res.status_code == 200
    assert "html" in prev_res.json()

    # 6. Approve Resume
    appr_res = await async_client.post(f"/api/v1/resumes/{resume_id}/approve", headers=auth_headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["version_number"] == 1

    # 7. List Versions
    ver_res = await async_client.get(f"/api/v1/resumes/{resume_id}/versions", headers=auth_headers)
    assert ver_res.status_code == 200
    assert len(ver_res.json()) >= 1

    # 8. Export Resume (PDF & DOCX)
    export_payload = {"format": "pdf", "validate_extraction": True}
    exp_res = await async_client.post(f"/api/v1/resumes/{resume_id}/export", json=export_payload, headers=auth_headers)
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["format"] == "pdf"
    assert exp_data["file_size_bytes"] > 0
    assert len(exp_data["sha256_checksum"]) == 64

    # 9. Duplicate Resume
    dup_res = await async_client.post(f"/api/v1/resumes/{resume_id}/duplicate", headers=auth_headers)
    assert dup_res.status_code == 200
    assert "Copy" in dup_res.json()["title"]

    # 10. Delete Duplicated Resume
    dup_id = dup_res.json()["id"]
    del_res = await async_client.delete(f"/api/v1/resumes/{dup_id}", headers=auth_headers)
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_job_description_analysis_and_tailoring(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Analyze Job Description
    job_payload = {
        "raw_text": "Looking for a Python Systems Engineer with Linux and FastAPI skills.",
        "job_title": "Systems Engineer",
        "employer": "TechGlobal",
    }
    analyze_res = await async_client.post("/api/v1/job-descriptions/analyze", json=job_payload, headers=auth_headers)
    assert analyze_res.status_code == 200
    job_snap = analyze_res.json()
    assert job_snap["job_title"] == "Systems Engineer"

    # 2. Create and Tailor Resume
    create_res = await async_client.post(
        "/api/v1/resumes",
        json={"title": "Tailoring Target Resume", "resume_type": "job_tailored"},
        headers=auth_headers,
    )
    resume_id = create_res.json()["id"]

    tailor_payload = {
        "resume_id": resume_id,
        "job_description_text": "Need Python, FastAPI, and Kubernetes skills.",
        "target_role": "Python Backend Engineer",
    }
    tailor_res = await async_client.post(f"/api/v1/resumes/{resume_id}/tailor", json=tailor_payload, headers=auth_headers)
    assert tailor_res.status_code == 200
    tailor_data = tailor_res.json()
    assert "evidence_mappings" in tailor_data
    assert len(tailor_data["evidence_mappings"]) > 0


@pytest.mark.asyncio
async def test_portfolios_api_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create Portfolio
    port_payload = {
        "title": "Principal Architect Portfolio",
        "professional_intro": "Experienced builder of scalable distributed systems.",
        "selected_skills": ["Python", "Linux"],
    }
    create_res = await async_client.post("/api/v1/portfolios", json=port_payload, headers=auth_headers)
    assert create_res.status_code in [200, 201]
    port_id = create_res.json()["id"]

    # 2. Get Portfolio
    get_res = await async_client.get(f"/api/v1/portfolios/{port_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Principal Architect Portfolio"

    # 3. Export Portfolio PDF
    exp_pdf = await async_client.post(f"/api/v1/portfolios/{port_id}/export/pdf", headers=auth_headers)
    assert exp_pdf.status_code == 200
    assert exp_pdf.json()["format"] == "pdf"

    # 4. Export Portfolio HTML
    exp_html = await async_client.post(f"/api/v1/portfolios/{port_id}/export/html", headers=auth_headers)
    assert exp_html.status_code == 200
    assert exp_html.json()["format"] == "html"
