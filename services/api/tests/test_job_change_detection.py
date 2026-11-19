"""Tests for Stage 30 job change detection, semantic normalization, and classification."""

import pytest
from app.recruitment.monitoring.changes.detection import detect_job_changes
from app.recruitment.monitoring.changes.semantic import (
    compute_content_hash,
    is_material_description_change,
    normalize_content,
)
from app.recruitment.monitoring.contracts import JobChangeType


def test_semantic_normalization_strips_html_and_whitespace():
    raw_html = "<p>We are hiring a <strong>Senior Backend Engineer</strong>.</p>\n\n  <div>Remote OK</div>"
    normalized = normalize_content(raw_html)
    assert normalized == "we are hiring a senior backend engineer . remote ok"


def test_content_hashing_consistency():
    text1 = "Python, FastAPI, Postgres, Docker."
    text2 = "  <p>Python,   FastAPI, Postgres, Docker.  </p>  "
    assert compute_content_hash(text1) == compute_content_hash(text2)


def test_material_vs_formatting_change():
    original = "<p>Qualifications: 5+ years experience with Python and AWS.</p>"
    # Whitespace and formatting only
    formatting_only = "<div>   Qualifications: 5+ years experience with Python and AWS. </div>"
    assert is_material_description_change(original, formatting_only) is False

    # Actual requirement addition
    material_change = "<p>Qualifications: 5+ years experience with Python, AWS, and Rust.</p>"
    assert is_material_description_change(original, material_change) is True


def test_detect_new_vacancy():
    new_job = {"id": "job_123", "title": "Software Engineer"}
    changes = detect_job_changes(old_job=None, new_data=new_job)
    assert len(changes) == 1
    assert changes[0].change_type == JobChangeType.NEW_VACANCY
    assert changes[0].is_material is True


def test_detect_job_closed_and_reopened():
    active_job = {"id": "job_123", "status": "active"}
    closed_job = {"id": "job_123", "status": "closed"}

    # Active -> Closed
    changes_closed = detect_job_changes(old_job=active_job, new_data=closed_job)
    assert any(c.change_type == JobChangeType.JOB_CLOSED for c in changes_closed)

    # Closed -> Active (Reopened)
    changes_reopened = detect_job_changes(old_job=closed_job, new_data=active_job)
    assert any(c.change_type == JobChangeType.JOB_REOPENED for c in changes_reopened)


def test_detect_salary_and_location_changes():
    old_job = {
        "id": "job_123",
        "salary_range": "$120,000 - $140,000",
        "location": "New York, NY",
        "work_arrangement": "hybrid",
    }
    new_job = {
        "id": "job_123",
        "salary_range": "$135,000 - $155,000",
        "location": "Remote - US",
        "work_arrangement": "remote",
    }
    changes = detect_job_changes(old_job=old_job, new_data=new_job)
    change_types = [c.change_type for c in changes]
    assert JobChangeType.SALARY_CHANGED in change_types
    assert JobChangeType.LOCATION_CHANGED in change_types
    assert JobChangeType.REMOTE_CONDITIONS_CHANGED in change_types
