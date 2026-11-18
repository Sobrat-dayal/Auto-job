"""Unit tests for Stage 22 contribution attribution and author vs committer evaluation."""

import pytest
from app.recruitment.github.contracts import (
    AttributionLevel,
    RepoVisibility,
    RepositoryMetadata,
)
from app.recruitment.github.contributions.attribution import ContributionAttributionEngine


@pytest.fixture
def sample_repo():
    return RepositoryMetadata(
        id="repo_sample",
        owner="applicant_user",
        name="portfolio-project",
        full_name="applicant_user/portfolio-project",
        html_url="https://github.com/applicant_user/portfolio-project",
        visibility=RepoVisibility.PUBLIC,
        is_fork=False,
        default_branch="main",
    )


@pytest.fixture
def forked_repo():
    return RepositoryMetadata(
        id="repo_fork",
        owner="applicant_user",
        name="upstream-lib",
        full_name="applicant_user/upstream-lib",
        html_url="https://github.com/applicant_user/upstream-lib",
        visibility=RepoVisibility.PUBLIC,
        is_fork=True,
        parent_repo="bigcorp/upstream-lib",
        default_branch="main",
    )


def test_evaluate_commits_applicant_match(sample_repo):
    raw_commits = [
        {
            "sha": "1111111111111111",
            "commit": {
                "message": "feat: add user authentication",
                "author": {"name": "Applicant", "email": "applicant@example.com", "date": "2026-11-18T10:00:00Z"},
                "committer": {"name": "Applicant", "email": "applicant@example.com", "date": "2026-11-18T10:00:00Z"},
            },
            "author": {"login": "applicant_user"},
            "parents": [{"sha": "00000000"}],
        },
        {
            "sha": "2222222222222222",
            "commit": {
                "message": "bump version to 1.2.0",
                "author": {"name": "dependabot[bot]", "email": "bot@github.com", "date": "2026-11-18T11:00:00Z"},
                "committer": {"name": "GitHub", "email": "noreply@github.com", "date": "2026-11-18T11:00:00Z"},
            },
            "author": {"login": "dependabot[bot]"},
            "parents": [{"sha": "11111111"}],
        },
    ]

    evaluated = ContributionAttributionEngine.evaluate_commits(sample_repo, raw_commits, applicant_login="applicant_user")
    assert len(evaluated) == 2

    # Applicant commit
    c1 = evaluated[0]
    assert c1.is_applicant is True
    assert c1.attribution_level == AttributionLevel.ACCOUNT_ATTRIBUTED_ACTIVITY

    # Bot commit
    c2 = evaluated[1]
    assert c2.is_applicant is False
    assert c2.attribution_level == AttributionLevel.REPOSITORY_ASSOCIATED


def test_evaluate_fork_attribution_lineage(forked_repo):
    raw_commits = [
        {
            "sha": "aaaa1111",
            "commit": {
                "message": "upstream original commit",
                "author": {"name": "Upstream Dev", "email": "dev@upstream.org", "date": "2025-01-01T00:00:00Z"},
            },
            "author": {"login": "upstream_dev"},
            "parents": [],
        },
        {
            "sha": "bbbb2222",
            "commit": {
                "message": "fix: bugfix contribution by applicant",
                "author": {"name": "Applicant", "email": "applicant@example.com", "date": "2026-11-18T12:00:00Z"},
            },
            "author": {"login": "applicant_user"},
            "parents": [{"sha": "aaaa1111"}],
        },
    ]

    evaluated = ContributionAttributionEngine.evaluate_commits(forked_repo, raw_commits, applicant_login="applicant_user")

    # Upstream commit must NOT be attributed to applicant
    up_c = next(c for c in evaluated if c.commit_sha == "aaaa1111")
    assert up_c.is_applicant is False
    assert up_c.attribution_level == AttributionLevel.REPOSITORY_ASSOCIATED

    # Applicant commit on fork IS attributed
    app_c = next(c for c in evaluated if c.commit_sha == "bbbb2222")
    assert app_c.is_applicant is True
    assert app_c.attribution_level == AttributionLevel.ACCOUNT_ATTRIBUTED_ACTIVITY


def test_evaluate_pull_requests(sample_repo):
    raw_prs = [
        {
            "number": 42,
            "title": "Implement core agent event bus",
            "user": {"login": "applicant_user"},
            "state": "closed",
            "merged_at": "2026-11-18T14:00:00Z",
            "created_at": "2026-11-18T10:00:00Z",
            "additions": 350,
            "deletions": 20,
            "changed_files": 5,
        },
        {
            "number": 43,
            "title": "Automated security updates",
            "user": {"login": "dependabot[bot]"},
            "state": "open",
            "merged_at": None,
            "created_at": "2026-11-18T15:00:00Z",
            "additions": 2,
            "deletions": 2,
            "changed_files": 1,
        },
    ]

    prs = ContributionAttributionEngine.evaluate_pull_requests(sample_repo, raw_prs, applicant_login="applicant_user")
    assert len(prs) == 2

    pr42 = next(p for p in prs if p.pr_number == 42)
    assert pr42.is_applicant is True
    assert pr42.attribution_level == AttributionLevel.CONTRIBUTION_EVIDENCE

    pr43 = next(p for p in prs if p.pr_number == 43)
    assert pr43.is_applicant is False
    assert pr43.attribution_level == AttributionLevel.REPOSITORY_ASSOCIATED
