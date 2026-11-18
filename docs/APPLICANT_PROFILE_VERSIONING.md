# AUTONOM Profile Versioning, Concurrency & Export (Stage 21)

## 1. Optimistic Concurrency Control (OCC)

In a multi-agent system where background agents (like `ResumeAgent` or `JobMatchingAgent`) and the desktop UI interact with applicant data simultaneously, race conditions must be prevented.

### 1.1 Concurrency Protocol
1. Every `ApplicantProfile` possesses a numeric `version` counter starting at 1.
2. Mutating requests (e.g. `PATCH /api/v1/applicants/{profile_id}`, `PATCH /api/v1/applicants/{profile_id}/identity`) accept an optional `expected_version` parameter.
3. If `expected_version` is supplied and does not match `profile.version`, the service raises `ConcurrencyConflictError` (HTTP 409 Conflict):
   ```json
   {
     "detail": "Version conflict: Expected version 2, but profile is at version 3."
   }
   ```
4. On every successful mutation, `profile.version` is incremented by 1, and `updated_at` is updated to current UTC time.

---

## 2. Immutable Audit History (`ProfileVersionRecord`)

Every mutation creates an immutable audit record:
- `version`: The revision number created by this change.
- `changed_fields`: List of attributes mutated (e.g. `["contact", "location"]`).
- `actor_id`: Identity of the actor responsible (`autonom-desktop-local`, `supervisor_agent`, user client ID).
- `reason`: Rationale or action label (e.g. `"Updated profile identity"`).
- `timestamp`: UTC timestamp.

Version history can be queried at any time via `GET /api/v1/applicants/{profile_id}/versions`.

---

## 3. Portable Profile Export

Users retain full data ownership. The entire profile, its atomic claim registry, and quality metrics can be exported as a comprehensive JSON archive via `POST /api/v1/applicants/{profile_id}/export`:

```json
{
  "exported_at": "2026-11-18T14:20:00Z",
  "profile": {
    "id": "prof_primary_applicant",
    "display_label": "Senior Systems Architect",
    "version": 4,
    "contact": { ... },
    "education": [ ... ],
    "experience": [ ... ],
    "skills": [ ... ],
    "projects": [ ... ]
  },
  "claims": [
    {
      "claim_id": "clm_123",
      "category": "degree",
      "normalized_value": "Degree: MS CS from UT Austin",
      "verification_status": "user_confirmed"
    }
  ],
  "quality": {
    "completeness_score": 92.5,
    "is_recruitment_ready": true,
    "issues": []
  }
}
```
