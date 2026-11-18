"""Unit tests for Stage 22 GitHub contracts, enums, and data models."""

import pytest
from app.recruitment.github.contracts import (
    ArchitectureType,
    AttributionLevel,
    CandidateProject,
    CandidateSkill,
    CandidateStatus,
    CommitEvidence,
    ConnectionMode,
    ConnectionStatus,
    ContributionFinding,
    DetectionConfidence,
    FileContentSnippet,
    GitHubConnection,
    GitHubDiagnostics,
    PullRequestEvidence,
    RepositoryArchitecture,
    RepositoryMetadata,
    RepoVisibility,
    SourceTreeEntry,
    SyncJobRecord,
    SyncStatus,
    TechCategory,
    TechnologyFinding,
)


def test_github_connection_defaults_and_validation():
    conn = GitHubConnection(
        id="ghc_test_01",
        login="octocat",
        github_id=583231,
        mode=ConnectionMode.PERSONAL_ACCESS_TOKEN,
        scopes=["repo:status", "public_repo"],
        can_access_private=True,
        public_repos_count=10,
    )
    assert conn.id == "ghc_test_01"
    assert conn.login == "octocat"
    assert conn.status == ConnectionStatus.NOT_CONNECTED
    assert conn.can_access_private is True
    assert "repo:status" in conn.scopes


def test_repository_metadata_model():
    repo = RepositoryMetadata(
        id="repo_autonom",
        owner="octocat",
        name="autonom",
        full_name="octocat/autonom",
        html_url="https://github.com/octocat/autonom",
        visibility=RepoVisibility.PUBLIC,
        is_fork=False,
        default_branch="main",
        languages={"Rust": 100000, "Python": 50000},
        topics=["ai", "agents", "rust"],
        stars_count=120,
    )
    assert repo.full_name == "octocat/autonom"
    assert repo.is_selected is False
    assert repo.allow_source_inspection is False
    assert repo.sync_status == SyncStatus.NOT_SYNCED
    assert repo.languages["Rust"] == 100000


def test_technology_finding_model():
    finding = TechnologyFinding(
        name="FastAPI",
        category=TechCategory.FRAMEWORK,
        version="0.115.0",
        confidence=DetectionConfidence.STRONGLY_SUPPORTED,
        evidence_source="pyproject.toml:tool.poetry.dependencies",
        repo_id="repo_api",
    )
    assert finding.name == "FastAPI"
    assert finding.category == TechCategory.FRAMEWORK
    assert finding.confidence == DetectionConfidence.STRONGLY_SUPPORTED


def test_commit_evidence_attribution():
    commit = CommitEvidence(
        commit_sha="a1b2c3d4e5f67890",
        message="feat: implement multi-agent supervisor loop",
        author_name="Sobrat",
        author_email="sobrat@example.com",
        author_login="sobrat",
        committed_date="2026-11-18T12:00:00Z",
        repo_id="repo_autonom",
        is_applicant=True,
        attribution_level=AttributionLevel.COMMIT_AUTHOR_EVIDENCE,
    )
    assert commit.is_applicant is True
    assert commit.attribution_level == AttributionLevel.COMMIT_AUTHOR_EVIDENCE


def test_candidate_skill_and_project():
    skill = CandidateSkill(
        id="csk_01",
        name="PostgreSQL",
        category=TechCategory.DATABASE,
        proficiency_hint="advanced",
        evidence_repo_id="repo_01",
        evidence_repo_name="autonom-db",
        confidence=DetectionConfidence.STRONGLY_SUPPORTED,
    )
    assert skill.status == CandidateStatus.AWAITING_REVIEW
    assert skill.proficiency_hint == "advanced"

    project = CandidateProject(
        id="cpj_01",
        title="autonom-db",
        description="Database migrations and storage engine",
        repo_id="repo_01",
        repo_name="autonom-db",
        repo_url="https://github.com/octocat/autonom-db",
        technologies=["PostgreSQL", "SQLAlchemy"],
        architecture_type=ArchitectureType.BACKEND_API,
        stars=42,
    )
    assert project.status == CandidateStatus.AWAITING_REVIEW
    assert "PostgreSQL" in project.technologies
