# Employment Eligibility & Work Authorization Matching

## 1. Work Authorization Safeguards (Required Test 139)
- Engine strictly verifies explicit country work authorizations declared in applicant profile (`authorized_countries`).
- **Demographic Inferences Strictly Prohibited**: The engine NEVER infers work authorization or citizenship from applicant's city of residence, telephone area code, educational institution, nationality, or surname.
- If work authorization is unverified or blank:
  - Requirement evaluated as `UNKNOWN`.
  - Item routed to Human Review Queue (`ReviewType.UNKNOWN_WORK_AUTH`).
  - Overall outcome marked `REQUIRES_APPLICANT_REVIEW` (Readiness: `REQUIRES_REVIEW`).

## 2. Visa Sponsorship Conflicts (Required Test 140)
- If applicant requires visa sponsorship (`requires_sponsorship=True`) and job posting explicitly states sponsorship is refused or not offered (`visa_sponsorship_refused=True` or `visa_sponsorship_offered=False`):
  - Hard constraint is violated (`hard_policy_passed=False`).
  - Evaluation produces `REJECTED_BY_HARD_POLICY`.
  - Irreversible: cannot be overridden by high relevance index or skill matches.
