# Recruitment Writing Security & Privacy Architecture

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

Recruitment writing involves highly confidential personal, legal, financial, and demographic data. AUTONOM's security architecture ensures that all writing generation, screening answers, and attestation logs adhere to local-first privacy, strict authorization, and complete isolation boundaries.

---

### Key Security Controls

1. **Local-First Processing**:
   - All applicant profiles, draft letters, screening answers, and reusable templates reside in local SQLite databases and local filesystem directories.
   - No data is transmitted to third-party ATS platforms or unvetted cloud storage without explicit user action.

2. **Bearer Token Authentication & Tenant Isolation**:
   - All REST API endpoints under `/api/v1/writing` require valid `Bearer <token>` authentication via FastAPI's `get_current_user` dependency.
   - The user's verified identity (`AuthContext.user_id`) scopes every database query. Candidates cannot inspect or modify writing artifacts belonging to other accounts.

3. **Protection of Sensitive EEO & Demographic Data**:
   - Protected categories (race, ethnicity, disability, gender, veteran status) are flagged with `sensitive_optional`.
   - Never stored in plain text alongside general profile summaries.
   - Scrubbed from public resume exports and cover letters unless explicitly requested by the applicant.

4. **Cryptographic Integrity & SHA-256 Digesting**:
   - Cover letter versions and approved packages compute SHA-256 digests over all structured content blocks and metadata.
   - Prevents tampering or undetected corruption of application documents.

5. **Safe File Handling & Path Traversal Prevention**:
   - Exported DOCX, PDF, and JSON packages are written to the application artifacts directory using sanitized UUID filenames.
   - Arbitrary path inputs (`../`) are strictly blocked by path resolution guards.

6. **Scope Boundary Enforcement**:
   - The Stage 24 writing engine **NEVER** interacts with external recruiters, sends emails, or performs automated headless browser form submissions.
   - Application packages are generated and stored locally for human approval, strictly adhering to Stage 24 roadmap boundaries.
