# Stage 22: GitHub Contribution Attribution Engine

## 1. The Attribution Challenge

Public repositories and team projects frequently present attribution ambiguities:
- **Author vs. Committer**: A developer may author code that is rebased or committed by a team lead, or vice versa.
- **Squash-and-Merge**: Multiple commits squashed into a single PR merge commit may lose individual commit author metadata unless the PR body or co-author trailers are inspected.
- **Forks and Lineage**: An applicant forking an established 10,000-commit repository must **not** be credited with the work of original authors.
- **Automated Bots**: Commits by Dependabot, Renovate, GitHub Actions, or semantic-release must be filtered out.

The `ContributionAttributionEngine` resolves these issues through multi-dimensional correlation.

---

## 2. Multi-Signal Identity Matching

The engine correlates commit metadata against the applicant's verified identities:
- GitHub Login handle (e.g., `octocat`).
- Profile primary and secondary email addresses.
- Known Git author display names.

```python
is_author_match = (
    author_login.lower() == applicant_login.lower() or
    author_email.lower() in applicant_emails
)
is_committer_match = (
    committer_login.lower() == applicant_login.lower() or
    committer_email.lower() in applicant_emails
)
```

### 2.1 Bot Exclusion
Any commit or pull request associated with recognized bot patterns (`*bot*`, `[bot]`, `github-actions[bot]`, `dependabot[bot]`, `renovate[bot]`) is tagged with `is_bot=True` and excluded from technical skill attribution.

### 2.2 Fork & Upstream Lineage Separation
When analyzing a repository marked with `is_fork=True`:
1. If the commit author does **not** match the applicant's login or email, the attribution level is strictly downgraded to `REPOSITORY_ASSOCIATED`.
2. Only commits explicitly authored by the applicant within the fork are elevated to `COMMIT_AUTHOR_EVIDENCE` or higher.
3. Upstream baseline code is never credited to the applicant as original architecture.

---

## 3. The 6-Tier Attribution Confidence Hierarchy

| Confidence Level | Description & Verification Standard |
| :--- | :--- |
| **`REPOSITORY_ASSOCIATED`** | The code exists within a repository associated with the applicant (e.g., starred, contributed by others on a shared team, or upstream fork code). Zero proof of individual authorship. |
| **`ACCOUNT_ATTRIBUTED_ACTIVITY`** | Activity registered to the applicant's account (e.g., repository creation, issue comment, PR review event). |
| **`COMMIT_AUTHOR_EVIDENCE`** | Verified commit where Git `author` email and login match the applicant's verified identity. Includes commit SHA, message, and diff stats. |
| **`CONTRIBUTION_EVIDENCE`** | Merged pull request authored by the applicant with code review approval and resolved issues. |
| **`APPLICANT_CONFIRMED_CONTRIBUTION`** | The applicant has explicitly confirmed the contribution claim through the Stage 22 desktop review queue. |
| **`INDEPENDENTLY_CORROBORATED`** | Contribution verified by third-party corroboration (e.g., external code reviews, co-authors, or institutional sponsorship). |
