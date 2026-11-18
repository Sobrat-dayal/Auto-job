"""End-to-End REST API Integration Tests for Recruitment Writing Endpoints (Stage 24)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_writing_overview_and_templates(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Overview
    res = await async_client.get("/api/v1/recruitment/writing/overview", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_cover_letters" in data
    assert "total_screening_questions" in data
    assert "approved_library_answers" in data

    # 2. Templates
    tpl_res = await async_client.get("/api/v1/cover-letter-templates", headers=auth_headers)
    assert tpl_res.status_code == 200
    templates = tpl_res.json()
    assert len(templates) >= 6
    assert any(t["id"] == "classic_professional" for t in templates)


@pytest.mark.asyncio
async def test_cover_letter_api_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create Cover Letter
    create_payload = {
        "title": "Backend Engineer Letter - Stripe",
        "target_role": "Backend Engineer",
        "employer_name": "Stripe",
        "letter_type": "role_specific",
        "template_id": "classic_professional",
        "tone": "professional",
        "length_preference": "standard",
    }
    create_res = await async_client.post("/api/v1/cover-letters", json=create_payload, headers=auth_headers)
    assert create_res.status_code in (200, 201)
    cl = create_res.json()
    letter_id = cl["id"]
    assert cl["target_role"] == "Backend Engineer"
    assert len(cl["blocks"]) >= 5

    # 2. Get Cover Letter
    get_res = await async_client.get(f"/api/v1/cover-letters/{letter_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == letter_id

    # 3. Patch Cover Letter
    patch_res = await async_client.patch(
        f"/api/v1/cover-letters/{letter_id}",
        json={"title": "Senior Backend Engineer Letter - Stripe"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Senior Backend Engineer Letter - Stripe"

    # 4. Rewrite Paragraph
    block_id = cl["blocks"][2]["id"]  # opening block
    rewrite_res = await async_client.post(
        f"/api/v1/cover-letters/{letter_id}/rewrite-paragraph",
        json={"block_id": block_id, "instruction": "make concise"},
        headers=auth_headers,
    )
    assert rewrite_res.status_code == 200

    # 5. Validate Grounding
    val_res = await async_client.post(f"/api/v1/cover-letters/{letter_id}/validate", headers=auth_headers)
    assert val_res.status_code == 200
    assert "is_valid" in val_res.json()

    # 6. Preview HTML
    prev_res = await async_client.get(f"/api/v1/cover-letters/{letter_id}/preview", headers=auth_headers)
    assert prev_res.status_code == 200
    assert "html" in prev_res.json()

    # 7. Approve Cover Letter
    appr_res = await async_client.post(f"/api/v1/cover-letters/{letter_id}/approve", headers=auth_headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["version_number"] == 1
    assert len(appr_res.json()["content_hash"]) == 64

    # 8. List Versions
    ver_res = await async_client.get(f"/api/v1/cover-letters/{letter_id}/versions", headers=auth_headers)
    assert ver_res.status_code == 200
    assert len(ver_res.json()) >= 1

    # 9. Export PDF & DOCX
    exp_res = await async_client.post(
        f"/api/v1/cover-letters/{letter_id}/export",
        json={"format": "pdf", "validate_extraction": True},
        headers=auth_headers,
    )
    assert exp_res.status_code == 200
    assert exp_res.json()["file_size_bytes"] > 0
    assert len(exp_res.json()["sha256_checksum"]) == 64

    # 10. Delete
    del_res = await async_client.delete(f"/api/v1/cover-letters/{letter_id}", headers=auth_headers)
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_questions_and_answers_api_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Parse Questions
    raw_text = "1. How many years of Python experience do you have?\n2. Are you authorized to work in the US? (Yes/No)"
    parse_res = await async_client.post(
        "/api/v1/application-questions/analyze",
        json={"raw_text": raw_text},
        headers=auth_headers,
    )
    assert parse_res.status_code == 200
    parsed = parse_res.json()
    assert len(parsed) >= 2

    # 2. Create Question Set
    qset_payload = {
        "job_title": "Platform Engineer",
        "employer": "CloudScale",
        "title": "Platform Screening 2026",
        "questions_raw": [
            "How many years of Python experience do you have?",
            "I certify that all statements are true.",
        ],
    }
    qset_res = await async_client.post("/api/v1/application-question-sets", json=qset_payload, headers=auth_headers)
    assert qset_res.status_code in (200, 201)
    qset = qset_res.json()
    set_id = qset["id"]

    # 3. Generate Answers
    gen_res = await async_client.post(
        f"/api/v1/application-question-sets/{set_id}/generate-answers",
        headers=auth_headers,
    )
    assert gen_res.status_code == 200
    qset_updated = gen_res.json()
    assert len(qset_updated["questions"]) == 2

    q1 = qset_updated["questions"][0]
    q2_att = qset_updated["questions"][1]
    assert q1["current_answer"] is not None
    # Attestation question should require user attestation
    assert q2_att["current_answer"]["state"] == "requires_user_attestation"

    # 4. Attest question
    att_res = await async_client.post(
        f"/api/v1/application-questions/{q2_att['id']}/attest",
        json={"attestation_accepted": True, "actor_id": "test_user"},
        headers=auth_headers,
    )
    assert att_res.status_code == 200
    assert att_res.json()["boolean_value"] is True
    assert att_res.json()["user_attestation_timestamp"] is not None


@pytest.mark.asyncio
async def test_answer_library_and_packages_api_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create Answer Library Entry
    lib_payload = {
        "title": "FastAPI Microservices",
        "category": "technical",
        "parameterized_template": "I have built REST APIs with {technology} in {project}.",
        "sample_resolved_text": "Sample",
        "applicable_technologies": ["FastAPI", "Python"],
    }
    lib_res = await async_client.post("/api/v1/application-answer-library", json=lib_payload, headers=auth_headers)
    assert lib_res.status_code in (200, 201)
    entry = lib_res.json()
    entry_id = entry["id"]

    # 2. Preview Reuse
    reuse_res = await async_client.post(
        f"/api/v1/application-answer-library/{entry_id}/reuse-preview",
        json={
            "question_text": "Describe your API experience.",
            "parameters": {"technology": "FastAPI", "project": "Payment Gateway"},
        },
        headers=auth_headers,
    )
    assert reuse_res.status_code == 200
    assert "Payment Gateway" in reuse_res.json()["resolved_text"]

    # 3. Create Writing Package
    pkg_payload = {
        "target_job_title": "Backend Architect",
        "target_employer": "FinTech Corp",
    }
    pkg_res = await async_client.post("/api/v1/application-writing-packages", json=pkg_payload, headers=auth_headers)
    assert pkg_res.status_code in (200, 201)
    pkg = pkg_res.json()
    pkg_id = pkg["id"]

    # 4. Validate Package
    val_res = await async_client.post(f"/api/v1/application-writing-packages/{pkg_id}/validate", headers=auth_headers)
    assert val_res.status_code == 200
    assert val_res.json()["is_ready"] is True

    # 5. Approve Package
    appr_res = await async_client.post(f"/api/v1/application-writing-packages/{pkg_id}/approve", headers=auth_headers)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "approved"
