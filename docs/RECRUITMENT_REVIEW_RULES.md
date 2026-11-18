# AUTONOM Recruitment Review Triggers & Rules

## Stage 25 of 50 — Human Review Queue Architecture

---

### Review Triggers

When an opportunity encounters an ambiguous or sensitive policy condition, it is not rejected outright; instead, it is placed in the Human Review Queue with tagged triggers:

| Trigger Code | Cause | Resolution Action |
|---|---|---|
| `COMPENSATION_UNDISCLOSED` | Job listing omits salary numbers. | User confirms whether to proceed. |
| `COMPENSATION_BELOW_FLOOR` | Stated salary is marginally below target. | User approves exception or drops. |
| `EMPLOYER_AMBIGUOUS` | Company shares tokens with multiple entities. | User verifies legal employer entity. |
| `WORK_AUTH_UNCERTAIN` | Target country lacks verified citizenship or visa. | User supplies legal attestation. |
| `EXPERIENCE_BELOW_THRESHOLD` | Candidate experience is within 1 year of required. | User decides whether to apply. |
| `UNVERIFIED_QUALIFICATIONS_REQUESTED` | Specific niche tool requested is not in profile. | User adds claim or omits. |
| `SENSITIVE_QUESTION_DETECTED` | Clearance, criminal history, or non-compete questions. | Explicit user sign-off required. |
| `MODE_2_DEFAULT_REVIEW` | Standard Mode 2 checkpoint prior to final submission. | User reviews document bundle. |
| `BUDGET_THRESHOLD_WARNING` | Daily or weekly budget at 90% utilization. | User acknowledges consumption. |
| `POLICY_CONFLICT_DETECTED` | Conflicting strategy rules detected. | User resolves conflict. |

---

### Resolution Lifecycle

Items remain in status `pending` until resolved:
- **`approve`**: Job proceeds to document preparation.
- **`reject`**: Job is logged as user-rejected and removed from pipeline.
- **`dismiss`**: Job is archived with reason.
