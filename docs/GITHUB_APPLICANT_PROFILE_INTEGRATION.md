# Stage 22: GitHub to Applicant Profile Integration & HITL Review

## 1. Zero Silent Mutation Mandate

Under no circumstances does the GitHub Intelligence Engine directly write into the canonical `ApplicantProfile` or modify verified skills without human interaction.

```
       [Raw GitHub Data]
       (Repos, Manifests, Commits, PRs)
              │
              v
       [CandidateGenerator]
       Transforms findings into provisional proposals
              │
              v
       +-------------------------------+
       |    Candidate Review Queue     |
       |  (Status = AWAITING_REVIEW)   |
       +-------------------------------+
              │
              ├────── Reject ──────────> [CandidateStatus.REJECTED] (Discarded)
              │
              ├────── Modify ──────────> [CandidateStatus.MODIFIED] (Applicant edits name/years/level)
              │
              v
       [User Clicks "Accept / Confirm"]
              │
              v
       +-------------------------------+
       |     CandidateReviewManager    |
       +-------------------------------+
              │
              ├─> 1. Stage 21 ApplicantProfileService.add_or_update_skill()
              ├─> 2. Stage 21 ApplicantProfileService.add_project()
              └─> 3. Stage 21 ClaimRegistry.register_claim()
                     (Status: VERIFIED, Provenance: GITHUB)
```

---

## 2. Candidate Generation

### 2.1 Skill Candidates (`CandidateSkill`)
- Generated from detected languages, manifest frameworks, databases, and containerization findings.
- **Proficiency Estimation**: Grounded in repository bytes, commit count, and recency of commits (e.g., repository active in past 6 months with $>50$ commits yields an initial estimate of `ADVANCED` or `INTERMEDIATE`).
- Includes `evidence_summary` detailing exact manifest files and commit counts.

### 2.2 Project Candidates (`CandidateProject`)
- Generated from selected repositories where the applicant demonstrated verified contributions or ownership.
- Includes repository description, primary technology stack tags, GitHub URL, star count, and architecture archetype.

---

## 3. Human-in-the-Loop Desktop Interface

The **Candidates Tab** (`GitHubCandidatesTab.tsx`) in the Desktop Workspace presents two distinct review queues:
1. **Skill Candidates Queue**:
   - Displays Candidate Skill Name, Category, Proficiency Hint, Evidence Source, and Associated Repository.
   - **Actions**:
     - **Accept**: Calls `/api/v1/github/skill-candidates/{id}/confirm`, atomically promoting the skill into the verified applicant profile.
     - **Reject**: Calls `/api/v1/github/candidates/{id}/reject`, discarding the candidate without modifying the profile.
2. **Project Candidates Queue**:
   - Displays Project Name, Role/Contribution summary, Technology Badges, and Star Count.
   - **Actions**:
     - **Accept Project**: Promotes the repository into the applicant's verified Portfolio Projects section in Stage 21.
     - **Reject Project**: Suppresses the repository from appearing in recruiter-facing resumes.

---

## 4. Atomic Claim Registration

When a candidate item is accepted, `CandidateReviewManager` invokes the Stage 21 `ClaimRegistry`:
- **Claim Subject**: `Skill: FastAPI` or `Project: autonom-core`.
- **Claim Type**: `TECHNICAL_SKILL` or `PROJECT_PORTFOLIO`.
- **Verification Level**: `EVIDENCE_BACKED` (attributed to Git commit SHAs and repository manifest proofs).
- **Source**: `GITHUB_API_STAGE_22`.
- **Created At**: Timestamped in UTC.
