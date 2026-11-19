"""Tests for Stage 30 Opportunity Queue prioritization, user actions, and Stage 31 readiness contract."""

from datetime import UTC, datetime
import pytest

from app.db.engine import async_session_factory
from app.recruitment.matching.contracts import (
    GapSeverity,
    GapType,
    JobMatchEvaluation,
    MatchingOutcome,
    SkillGapItem,
)
from app.recruitment.monitoring.contracts import (
    OpportunityPriority,
    OpportunityQueueStatus,
    OpportunityQueueUpdateRequest,
)
from app.recruitment.monitoring.opportunities.queue import OpportunityQueueManager
from app.recruitment.monitoring.opportunities.readiness import evaluate_preparation_readiness


def test_evaluate_preparation_readiness_eligible():
    job = {
        "id": "job_canon_123",
        "title": "Staff Backend Engineer",
        "company": "Acme Corp",
        "status": "active",
        "application_url": "https://example.com/apply",
    }
    evaluation = JobMatchEvaluation(
        id="eval_001",
        canonical_job_id="job_canon_123",
        job_title="Staff Backend Engineer",
        company_name="Acme Corp",
        profile_id="profile_456",
        relevance_index=92.5,
        eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        hard_policy_passed=True,
        gaps=[],
        missing_information=[],
        review_requests=[],
        evaluated_at=datetime.now(UTC),
        career_strategy_id="strat_789",
    )
    ready, candidate = evaluate_preparation_readiness(
        canonical_job=job,
        evaluation=evaluation,
        priority=OpportunityPriority.HIGH,
    )
    assert ready is True
    assert candidate is not None
    assert candidate.canonical_job_id == "job_canon_123"
    assert candidate.company_name == "Acme Corp"
    assert candidate.relevance_score == 92.5
    assert candidate.priority == OpportunityPriority.HIGH
    assert candidate.ready_for_preparation is True


def test_evaluate_preparation_readiness_blocked_by_gap():
    job = {
        "id": "job_canon_123",
        "title": "Backend Engineer",
        "company": "Acme Corp",
        "status": "active",
    }
    evaluation = JobMatchEvaluation(
        id="eval_002",
        canonical_job_id="job_canon_123",
        job_title="Backend Engineer",
        company_name="Acme Corp",
        profile_id="profile_456",
        relevance_index=50.0,
        eligibility_outcome=MatchingOutcome.KNOWN_REQUIREMENT_NOT_MET,
        hard_policy_passed=False,
        gaps=[
            SkillGapItem(
                skill_or_qualification="Security Clearance",
                gap_type=GapType.MISSING_MANDATORY_SKILL,
                severity=GapSeverity.BLOCKING,
                description="Active TS/SCI clearance required",
                remediation_suggestion="",
            )
        ],
        missing_information=[],
        review_requests=[],
        evaluated_at=datetime.now(UTC),
    )
    ready, candidate = evaluate_preparation_readiness(
        canonical_job=job,
        evaluation=evaluation,
        priority=OpportunityPriority.LOW,
    )
    assert ready is False
    assert candidate is None


def test_evaluate_preparation_readiness_closed_job():
    job = {
        "id": "job_canon_closed",
        "title": "Closed Role",
        "company": "Acme Corp",
        "status": "closed",
    }
    evaluation = JobMatchEvaluation(
        id="eval_003",
        canonical_job_id="job_canon_closed",
        job_title="Closed Role",
        company_name="Acme Corp",
        profile_id="profile_456",
        relevance_index=90.0,
        eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        hard_policy_passed=True,
        gaps=[],
        missing_information=[],
        review_requests=[],
        evaluated_at=datetime.now(UTC),
    )
    ready, candidate = evaluate_preparation_readiness(
        canonical_job=job,
        evaluation=evaluation,
        priority=OpportunityPriority.HIGH,
    )
    assert ready is False
    assert candidate is None


@pytest.mark.asyncio
async def test_opportunity_queue_upsert_and_user_actions():
    mgr = OpportunityQueueManager()
    job = {
        "id": "job_queue_test_001",
        "title": "Lead Software Engineer",
        "company": "TechCorp",
        "status": "active",
        "location": "Remote",
        "work_arrangement": "remote",
        "application_url": "https://example.com/apply",
    }
    eval_mock = JobMatchEvaluation(
        id="eval_queue_001",
        canonical_job_id="job_queue_test_001",
        job_title="Lead Software Engineer",
        company_name="TechCorp",
        profile_id="prof_001",
        relevance_index=88.0,
        eligibility_outcome=MatchingOutcome.ELIGIBLE_AND_ALIGNED,
        hard_policy_passed=True,
        gaps=[],
        missing_information=[],
        review_requests=[],
        evaluated_at=datetime.now(UTC),
        career_strategy_id="strat_001",
    )

    async with async_session_factory() as session:
        from app.db.models import JobListing, JobSource
        src = JobSource(
            id="src_queue_test_001",
            platform_name="test_platform",
            source_type="api",
            source_url="https://api.test.com",
            enabled=True,
        )
        session.add(src)
        listing = JobListing(
            id="job_queue_test_001",
            source_id="src_queue_test_001",
            external_id="ext_queue_001",
            title="Lead Software Engineer",
            company="TechCorp",
            application_url="https://example.com/apply",
            status="active",
        )
        session.add(listing)
        await session.flush()

        # Upsert
        entry = await mgr.upsert_entry(
            canonical_job=job,
            applicant_profile_id="prof_001",
            evaluation=eval_mock,
            career_strategy_id="strat_001",
            session=session,
        )
        assert entry.canonical_job_id == "job_queue_test_001"
        assert entry.company == "TechCorp"
        assert entry.relevance_score == 88.0

        # User Action: Save
        updated_saved = await mgr.update_entry(
            entry_id=entry.id,
            req=OpportunityQueueUpdateRequest(user_action="save"),
            session=session,
        )
        assert updated_saved.queue_status == OpportunityQueueStatus.SAVED

        # User Action: Prioritize
        updated_prio = await mgr.update_entry(
            entry_id=entry.id,
            req=OpportunityQueueUpdateRequest(user_action="prioritize"),
            session=session,
        )
        assert updated_prio.priority == OpportunityPriority.HIGH

        # User Action: Exclude
        updated_excl = await mgr.update_entry(
            entry_id=entry.id,
            req=OpportunityQueueUpdateRequest(user_action="exclude", notes="Not interested in role"),
            session=session,
        )
        assert updated_excl.queue_status == OpportunityQueueStatus.EXCLUDED
