"""Contribution Attribution and Authorship Intelligence Engine (Stage 22)."""

from __future__ import annotations

import logging
from typing import Optional

from app.recruitment.github.contracts import (
    AttributionLevel,
    CommitEvidence,
    ContributionFinding,
    PullRequestEvidence,
    RepositoryMetadata,
)

logger = logging.getLogger("autonom.recruitment.github.contributions.attribution")

BOT_IDENTIFIERS = {"dependabot", "github-actions", "renovate", "bot", "snyk"}


class ContributionAttributionEngine:
    """Evaluates commit metadata, PR history, fork lineage, and assigns strict attribution levels."""

    @classmethod
    def evaluate_commits(
        cls,
        repo: RepositoryMetadata,
        raw_commits: list[dict],
        applicant_login: str,
        applicant_emails: Optional[list[str]] = None,
    ) -> list[CommitEvidence]:
        evidences: list[CommitEvidence] = []
        user_emails = {e.lower().strip() for e in (applicant_emails or [])}
        user_login = applicant_login.lower().strip()

        for c in raw_commits:
            sha = c.get("sha", "")
            commit_info = c.get("commit", {})
            author_info = commit_info.get("author", {})
            committer_info = commit_info.get("committer", {})
            author_name = author_info.get("name", "Unknown")
            author_email = author_info.get("email", "")
            author_date = author_info.get("date", "")
            message = commit_info.get("message", "")

            # GitHub account association
            gh_author_login = c.get("author", {}).get("login", "").lower() if isinstance(c.get("author"), dict) else ""
            stats = c.get("stats", {})
            files = [f.get("filename") for f in c.get("files", []) if isinstance(f, dict)]

            is_bot = any(b in author_name.lower() or b in author_email.lower() or b in gh_author_login for b in BOT_IDENTIFIERS)

            # Attribution evaluation
            is_attributed = False
            level = AttributionLevel.REPOSITORY_ASSOCIATED

            if gh_author_login and gh_author_login == user_login:
                is_attributed = True
                level = AttributionLevel.ACCOUNT_ATTRIBUTED_ACTIVITY
            elif author_email.lower() in user_emails:
                is_attributed = True
                level = AttributionLevel.COMMIT_AUTHOR_EVIDENCE

            # If repo is a fork and commit was authored upstream by someone else, avoid attributing to applicant!
            if repo.is_fork and not is_attributed:
                level = AttributionLevel.REPOSITORY_ASSOCIATED

            is_squash = "squash" in message.lower() or "(#" in message
            is_merge = len(c.get("parents", [])) > 1

            evidence = CommitEvidence(
                sha=sha,
                repo_id=repo.id,
                author_name=author_name,
                author_email=author_email,
                author_date=author_date,
                committer_name=committer_info.get("name"),
                committer_date=committer_info.get("date"),
                message=message,
                is_merge=is_merge,
                is_squash=is_squash,
                additions=stats.get("additions", 0),
                deletions=stats.get("deletions", 0),
                total_changes=stats.get("total", 0),
                files_changed=files,
                attribution_level=level,
                is_applicant_attributed=is_attributed,
                is_bot=is_bot,
            )
            evidences.append(evidence)

        return evidences

    @classmethod
    def evaluate_pull_requests(
        cls,
        repo: RepositoryMetadata,
        raw_prs: list[dict],
        applicant_login: str,
    ) -> list[PullRequestEvidence]:
        pr_evidences: list[PullRequestEvidence] = []
        user_login = applicant_login.lower().strip()

        for pr in raw_prs:
            pr_num = pr.get("number", 0)
            author_login = pr.get("user", {}).get("login", "") if isinstance(pr.get("user"), dict) else ""
            is_attributed = (author_login.lower() == user_login)
            level = AttributionLevel.CONTRIBUTION_EVIDENCE if is_attributed else AttributionLevel.REPOSITORY_ASSOCIATED

            merged = bool(pr.get("merged_at"))
            pr_ev = PullRequestEvidence(
                pr_number=pr_num,
                repo_id=repo.id,
                title=pr.get("title", ""),
                description=pr.get("body"),
                author_login=author_login,
                state=pr.get("state", "closed"),
                merged=merged,
                merged_at=pr.get("merged_at"),
                merged_by=pr.get("merged_by", {}).get("login") if isinstance(pr.get("merged_by"), dict) else None,
                additions=pr.get("additions", 0),
                deletions=pr.get("deletions", 0),
                changed_files=pr.get("changed_files", 0),
                attribution_level=level,
                is_applicant_attributed=is_attributed,
            )
            pr_evidences.append(pr_ev)

        return pr_evidences

    @classmethod
    def generate_contribution_findings(
        cls,
        repo: RepositoryMetadata,
        commits: list[CommitEvidence],
        prs: list[PullRequestEvidence],
    ) -> list[ContributionFinding]:
        findings: list[ContributionFinding] = []

        # Attributed commits
        for c in commits:
            if c.is_applicant_attributed and not c.is_bot:
                first_line = c.message.splitlines()[0] if c.message else "Code contribution"
                findings.append(
                    ContributionFinding(
                        repo_id=repo.id,
                        activity_type="commit",
                        reference_id=c.sha[:8],
                        summary=f"Commit {c.sha[:7]}: {first_line}",
                        attribution_level=c.attribution_level,
                        timestamp=c.author_date,
                    )
                )

        # Attributed PRs
        for pr in prs:
            if pr.is_applicant_attributed:
                status_str = "Merged" if pr.merged else "Submitted"
                findings.append(
                    ContributionFinding(
                        repo_id=repo.id,
                        activity_type="pull_request",
                        reference_id=f"PR #{pr.pr_number}",
                        summary=f"{status_str} Pull Request #{pr.pr_number}: {pr.title}",
                        attribution_level=pr.attribution_level,
                        timestamp=pr.merged_at or "",
                    )
                )

        return findings
