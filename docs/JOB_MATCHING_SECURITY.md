# Security, Privacy & Compliance Architecture

## 1. Local Processing & Privacy Guarantees
- All applicant profile facts, work authorizations, and career preferences remain stored in local SQLite database on the user's Windows machine.
- No applicant demographic data or PII is transmitted to external endpoints for matching.
- Offline matching capability ensures evaluations execute with 100% functionality without internet access.

## 2. Authorization Boundaries
- Every REST API endpoint enforces Bearer token authentication against `settings.api_key`.
- Read and evaluate operations are logged in `job_match_audit_events` with actor attribution, event types, and timestamps.
- Zero autonomous submissions: The engine enforces a hard architectural boundary separating readiness for preparation from application submission.
