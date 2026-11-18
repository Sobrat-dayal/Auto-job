"""Unit tests for Stage 21 Applicant Profile Security, Scoped Redaction, and Authorization Enforcement."""

import pytest

from app.core.security import AuthContext
from app.recruitment.profile.contracts import (
    ApplicantProfile,
    ContactInfo,
    EducationRecord,
    EmploymentRecord,
    LocationInfo,
    ProjectRecord,
    SkillItem,
)
from app.recruitment.profile.errors import ProfilePermissionDeniedError
from app.recruitment.profile.integrations.agents import AgentProfileAdapter
from app.recruitment.profile.integrations.authorization import (
    SCOPE_PROFILE_EXPORT,
    SCOPE_PROFILE_READ,
    SCOPE_PROFILE_UPDATE,
    ProfileAuthorizationEnforcer,
)


@pytest.fixture
def populated_profile() -> ApplicantProfile:
    return ApplicantProfile(
        id="prof_sec_test",
        owner_id="applicant_user_1",
        display_label="Senior Cloud Engineer",
        status="active",
        version=1,
        contact=ContactInfo(
            legal_name="Alice Smith",
            preferred_name="Alice",
            primary_email="alice.smith@secret.org",
            phone="+1-555-0144",
        ),
        location=LocationInfo(
            city="Seattle",
            country="United States",
            remote_preference="flexible",
        ),
        skills=[
            SkillItem(id="sk_1", name="Python", canonical_name="python"),
            SkillItem(id="sk_2", name="AWS", canonical_name="aws"),
        ],
        education=[
            EducationRecord(id="ed_1", institution="University of Washington", degree="BS", field_of_study="CS")
        ],
        experience=[
            EmploymentRecord(
                id="em_1",
                employer="Cloud Systems Inc",
                job_title="Senior Engineer",
                start_date="2020-01",
                technologies=["Python", "AWS"],
            )
        ],
        projects=[
            ProjectRecord(
                id="pr_1",
                title="Cloud Mesh",
                description="Cloud Mesh service routing architecture",
                repository_url="https://github.com/alicesmith/cloud-mesh",
            )
        ],
    )


def test_job_matching_agent_redaction(populated_profile: ApplicantProfile):
    """Verifies that JobMatchingAgent never receives sensitive contact information."""
    snapshot = AgentProfileAdapter.get_job_matching_snapshot(populated_profile).filtered_data

    assert "skills" in snapshot
    assert len(snapshot["skills"]) == 2
    assert "location" in snapshot
    assert snapshot["location"]["city"] == "Seattle"

    # CRITICAL: Verify contact information is completely absent or redacted
    assert "contact" not in snapshot
    assert "primary_email" not in snapshot
    assert "phone" not in snapshot
    assert "legal_name" not in snapshot


def test_resume_agent_scoped_data(populated_profile: ApplicantProfile):
    """Verifies that ResumeAgent receives professional accomplishments but not unverified PII."""
    snapshot = AgentProfileAdapter.get_resume_snapshot(populated_profile).filtered_data

    assert "experience" in snapshot
    assert len(snapshot["experience"]) == 1
    assert snapshot["experience"][0]["employer"] == "Cloud Systems Inc"
    assert "skills" in snapshot
    assert "projects" in snapshot

    # Personal phone must not be in raw resume agent payload
    assert "phone" not in snapshot


def test_interview_prep_agent_scoped_data(populated_profile: ApplicantProfile):
    """Verifies that InterviewPrepAgent receives technical projects, repositories, and stack info."""
    snapshot = AgentProfileAdapter.get_interview_prep_snapshot(populated_profile).filtered_data

    assert "projects" in snapshot
    assert len(snapshot["projects"]) == 1
    assert snapshot["projects"][0]["title"] == "Cloud Mesh"
    assert "description" in snapshot["projects"][0]


def test_owner_isolation_enforcement(populated_profile: ApplicantProfile):
    """Verifies that another regular user cannot access an applicant profile they do not own."""
    # Legitimate owner
    owner_auth = AuthContext(client_id="applicant_user_1", authenticated=True, scopes=[SCOPE_PROFILE_READ])
    ProfileAuthorizationEnforcer.check_ownership(populated_profile, owner_auth)

    # Unauthorized different user
    intruder_auth = AuthContext(client_id="intruder_user_99", authenticated=True, scopes=[SCOPE_PROFILE_READ])
    with pytest.raises(ProfilePermissionDeniedError, match="belongs to another user"):
        ProfileAuthorizationEnforcer.check_ownership(populated_profile, intruder_auth)

    # Admin user can access
    admin_auth = AuthContext(client_id="admin", authenticated=True, scopes=[SCOPE_PROFILE_READ])
    ProfileAuthorizationEnforcer.check_ownership(populated_profile, admin_auth)


def test_permission_scope_enforcement():
    """Verifies that operations require their required authorization scopes."""
    auth_without_export = AuthContext(
        client_id="u1",
        authenticated=True,
        scopes=[SCOPE_PROFILE_READ, SCOPE_PROFILE_UPDATE],
    )
    with pytest.raises(ProfilePermissionDeniedError, match="Required scope .* is not granted"):
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_EXPORT, auth_without_export)

    auth_with_export = AuthContext(client_id="u1", authenticated=True, scopes=[SCOPE_PROFILE_EXPORT])
    ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_EXPORT, auth_with_export)
