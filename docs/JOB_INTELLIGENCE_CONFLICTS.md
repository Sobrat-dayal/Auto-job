# Multi-Source Requirement Conflicts & Reconciliation (Stage 28)

## 1. Overview
When a canonical vacancy is observed across multiple discovery sources (e.g. Greenhouse public board, employer career portal, and an aggregator feed), the descriptions may contain contradictory conditions.

## 2. Supported Conflict Types
- `WORK_ARRANGEMENT`: One source specifies 100% Remote, while another specifies Hybrid or Onsite.
- `SALARY_RANGE`: Distinct salary figures reported across providers.
- `VISA_SPONSORSHIP`: One provider advertises visa sponsorship while another states sponsorship is refused.
- `DEGREE_REQUIREMENT`: Contradictory degree prerequisites (e.g. Master's required vs. Bachelor's required vs. No degree needed).
- `EXPERIENCE_DURATION`: Disparate minimum years requirements.

## 3. Conflict Resolution Strategies
- `PENDING`: Awaiting human review or authority resolution.
- `HIGHER_AUTHORITY_ACCEPTED`: Reconciled by source authority hierarchy:
  - Official Employer Career Portal (Rank 100)
  - Direct ATS APIs (Greenhouse, Lever, Ashby - Rank 90)
  - Structured Feeds (Rank 70)
  - General Job Boards (Rank 50)
- `NEWER_SOURCE_ACCEPTED`: Reconciled by publication timestamp.
- `MANUAL_OVERRIDE`: Explicit resolution by an authorized user in the Human Review Queue.

## 4. Human Review Queue
Contradictions that cannot be resolved automatically with high confidence are routed to `job_intelligence_reviews` with `status = PENDING`. The Desktop UI enables side-by-side comparison and resolution.
