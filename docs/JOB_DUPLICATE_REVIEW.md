# Job Duplicate Human Review Queue (Stage 27)

## Overview
The Human Duplicate Review Queue manages borderline, ambiguous, or high-stakes duplicate candidates that fall within the threshold window ($0.75 \le \text{similarity} < 0.92$) or contain non-fatal discrepancies.

## Review Queue Operations
When an observation generates a candidate pair, a record is created in `job_duplicate_candidates` with status `proposed` and audit details in `job_duplicate_review_requests`.

### Supported Human Decisions
1. **Merge (`merge`)**:
   - Confirms that Job B is a duplicate of Job A.
   - Triggers `MergeExecutionEngine` to transactionally absorb Job B into Job A.
   - Creates alias redirects from Job B's ID to Job A's ID.
2. **Keep Separate (`keep_separate`)**:
   - Confirms that the two postings represent distinct vacancies.
   - Marks candidate pair as `confirmed_distinct`.
   - Prevents future automatic pairing between these two records.
3. **Mark Related (`mark_related`)**:
   - Recognizes that the jobs belong to the same team or company but represent separate openings (e.g., sister roles or pooled hiring).
   - Inserts relationship record into `canonical_job_relationships` (`similar_role`).
4. **Defer (`defer`)**:
   - Leaves candidate in queue for subsequent observation updates.

## Audit Logging
Every human review action records:
- `decided_by`: User or agent identifier (`user_manual` or agent identity).
- `reason`: Human justification string.
- `decided_at`: UTC timestamp stored in `job_duplicate_decisions`.
