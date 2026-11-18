"""Integration test suite for Stage 21 Applicant Profile FastAPI REST API endpoints."""

import pytest
from httpx import AsyncClient

from app.recruitment.profile.contracts import ProficiencyLevel, QualitySeverity, SkillCategory


@pytest.mark.asyncio
async def test_applicant_profile_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. List profiles (contains initial default profile)
    res = await async_client.get("/api/v1/applicants", headers=auth_headers)
    assert res.status_code == 200
    profiles = res.json()
    assert len(profiles) >= 1
    default_id = profiles[0]["id"]

    # 2. Get specific profile
    res = await async_client.get(f"/api/v1/applicants/{default_id}", headers=auth_headers)
    assert res.status_code == 200
    prof = res.json()
    assert prof["id"] == default_id

    # 3. Create a new custom profile
    create_payload = {
        "display_label": "Senior Systems Architect Profile",
        "owner_id": "default_user",
    }
    res = await async_client.post("/api/v1/applicants", json=create_payload, headers=auth_headers)
    assert res.status_code == 201
    created = res.json()
    profile_id = created["id"]
    assert created["display_label"] == "Senior Systems Architect Profile"
    assert created["version"] == 1

    # 4. Update Profile Metadata
    patch_meta = {
        "display_label": "Principal Systems Architect",
        "expected_version": 1,
    }
    res = await async_client.patch(f"/api/v1/applicants/{profile_id}", json=patch_meta, headers=auth_headers)
    assert res.status_code == 200
    updated_meta = res.json()
    assert updated_meta["display_label"] == "Principal Systems Architect"
    assert updated_meta["version"] == 2

    # 5. Update Identity & Eligibility
    identity_payload = {
        "contact": {
            "legal_name": "Marcus Aurelius Vance",
            "preferred_name": "Marc",
            "primary_email": "marc.vance@example.com",
            "phone": "+1 (555) 018-9922",
            "portfolio_url": "https://marcvance.dev",
        },
        "location": {
            "city": "Austin",
            "state_province": "TX",
            "country": "United States",
            "remote_preference": "flexible",
        },
        "eligibility": {
            "authorized_countries": ["United States"],
            "requires_sponsorship": False,
            "notice_period_days": 14,
            "confirmed_by_user": True,
        },
        "expected_version": 2,
    }
    res = await async_client.patch(f"/api/v1/applicants/{profile_id}/identity", json=identity_payload, headers=auth_headers)
    assert res.status_code == 200
    updated_ident = res.json()
    assert updated_ident["contact"]["legal_name"] == "Marcus Aurelius Vance"
    assert updated_ident["location"]["city"] == "Austin"
    assert updated_ident["version"] == 3

    # 6. Add Education
    edu_payload = {
        "id": "edu_ut_austin",
        "institution": "University of Texas at Austin",
        "degree": "Master of Science",
        "field_of_study": "Computer Science",
        "start_date": "2018-09",
        "end_date": "2020-05",
        "gpa": 3.95,
        "distinctions": ["Dean's Graduate Fellowship"],
    }
    res = await async_client.post(f"/api/v1/applicants/{profile_id}/education", json=edu_payload, headers=auth_headers)
    assert res.status_code == 201
    updated_edu = res.json()
    assert len(updated_edu["education"]) == 1
    assert updated_edu["education"][0]["institution"] == "University of Texas at Austin"

    # 7. Add Employment Experience
    exp_payload = {
        "id": "exp_cloud_dynamics",
        "employer": "Cloud Dynamics Inc",
        "job_title": "Lead Infrastructure Architect",
        "start_date": "2020-06",
        "is_current": True,
        "technologies": ["Go", "Rust", "Kubernetes", "AWS", "Terraform"],
        "achievements": [
            {
                "id": "ach_k8s_mig",
                "statement": "Orchestrated zero-downtime migration of 600+ microservices to Kubernetes.",
                "metric_value": "100%",
                "metric_unit": "uptime",
            }
        ],
    }
    res = await async_client.post(f"/api/v1/applicants/{profile_id}/experience", json=exp_payload, headers=auth_headers)
    assert res.status_code == 201
    updated_exp = res.json()
    assert len(updated_exp["experience"]) == 1
    assert updated_exp["experience"][0]["employer"] == "Cloud Dynamics Inc"

    # 8. Add Skill
    skill_payload = {
        "id": "sk_kubernetes",
        "name": "Kubernetes",
        "canonical_name": "kubernetes",
        "category": SkillCategory.CLOUD_DEVOPS,
        "proficiency": ProficiencyLevel.EXPERT,
        "years_experience": 6.0,
    }
    res = await async_client.post(f"/api/v1/applicants/{profile_id}/skills", json=skill_payload, headers=auth_headers)
    assert res.status_code == 200
    updated_sk = res.json()
    assert len(updated_sk["skills"]) == 1
    assert updated_sk["skills"][0]["name"] == "Kubernetes"

    # 9. Add Project
    proj_payload = {
        "id": "proj_k8s_mesh",
        "title": "HyperMesh Service Fabric",
        "description": "High-performance service mesh proxy written in Rust.",
        "repo_url": "https://github.com/marcvance/hypermesh",
        "technologies": ["Rust", "Tokio", "eBPF", "Kubernetes"],
    }
    res = await async_client.post(f"/api/v1/applicants/{profile_id}/projects", json=proj_payload, headers=auth_headers)
    assert res.status_code == 201
    updated_proj = res.json()
    assert len(updated_proj["projects"]) == 1

    # 10. Data Quality Report
    res = await async_client.get(f"/api/v1/applicants/{profile_id}/quality", headers=auth_headers)
    assert res.status_code == 200
    quality = res.json()
    assert quality["profile_id"] == profile_id
    assert quality["completeness_score"] >= 50.0

    # 11. Generate Scoped Agent Snapshot (JobMatchingAgent)
    snap_payload = {
        "target_agent": "JobMatchingAgent",
        "authorized_scopes": ["skills", "education"],
    }
    res = await async_client.post(f"/api/v1/applicants/{profile_id}/snapshot", json=snap_payload, headers=auth_headers)
    assert res.status_code == 200
    snap = res.json()
    assert snap["target_agent"] == "JobMatchingAgent"
    # Ensure sensitive contact details are redacted from JobMatchingAgent
    assert "contact" not in snap["filtered_data"]

    # 12. Export Profile
    res = await async_client.post(f"/api/v1/applicants/{profile_id}/export", headers=auth_headers)
    assert res.status_code == 200
    export_data = res.json()
    assert "profile" in export_data
    assert "claims" in export_data
    assert "quality" in export_data
