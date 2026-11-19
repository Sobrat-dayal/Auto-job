"""Unit tests for multi-source requirement conflict detection (Section 118)."""

import pytest

from app.recruitment.intelligence.contracts import (
    CompensationIntelligence,
    ConflictType,
    EligibilityConditions,
    EmploymentConditions,
    JobIntelligenceRecord,
    ReviewStatus,
    WorkplaceType,
)
from app.recruitment.intelligence.reconciliation.conflicts import detect_multi_source_conflicts


def test_workplace_and_salary_conflicts():
    rec_a = JobIntelligenceRecord(
        canonical_job_id="job-1",
        description_hash="hash-a",
        job_title="Software Engineer",
        employment_conditions=EmploymentConditions(workplace_type=WorkplaceType.REMOTE_GLOBAL),
        compensation=CompensationIntelligence(is_disclosed=True, base_min=120000.0, base_max=140000.0, currency="USD"),
        eligibility=EligibilityConditions(visa_sponsorship_offered=True),
    )

    rec_b = JobIntelligenceRecord(
        canonical_job_id="job-1",
        description_hash="hash-b",
        job_title="Software Engineer",
        employment_conditions=EmploymentConditions(workplace_type=WorkplaceType.HYBRID),
        compensation=CompensationIntelligence(is_disclosed=True, base_min=150000.0, base_max=180000.0, currency="USD"),
        eligibility=EligibilityConditions(visa_sponsorship_offered=False),
    )

    conflicts, reviews = detect_multi_source_conflicts(rec_a, rec_b, source_a_id="greenhouse", source_b_id="career_portal")

    conflict_types = [c.conflict_type for c in conflicts]
    assert ConflictType.WORK_ARRANGEMENT in conflict_types
    assert ConflictType.SALARY_RANGE in conflict_types
    assert ConflictType.VISA_SPONSORSHIP in conflict_types

    assert len(reviews) == 3
    for r in reviews:
        assert r.status == ReviewStatus.PENDING
