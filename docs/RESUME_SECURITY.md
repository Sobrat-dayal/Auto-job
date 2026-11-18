# AUTONOM — Resume & Portfolio Security Architecture (Stage 23)

## 1. Threat Model & Security Principles

Resume documents aggregate highly sensitive Personal Identifiable Information (PII) including legal names, contact numbers, email addresses, geographical residency, employment histories, and compensation signals.

AUTONOM enforces rigorous security controls across all Stage 23 subsystems:

### 1.1 Scope-Governed Authorization
All resume and portfolio endpoints require authenticated requests bearing appropriate scopes:
- `applicant.profile.read`: Required to inspect canonical profile facts for synthesis.
- `recruitment.resume.read`: Required to view resumes and inspect version snapshots.
- `recruitment.resume.write`: Required to create, patch, or tailor resumes.
- `recruitment.resume.export`: Required to generate binary files (.docx, .pdf).

The elevated local desktop client (`autonom-desktop-local`) is explicitly authorized to orchestrate compilation on behalf of the active local user.

### 1.2 Path Traversal & Injection Prevention
- Generated artifact paths use sanitized filenames and UUID tokens:
  ```python
  safe_filename = f"{re.sub(r'[^a-zA-Z0-9_-]', '_', doc.title)}_{doc.id}.pdf"
  ```
- File reads and writes are strictly jailed within `data/artifacts/resumes/` and `data/artifacts/portfolios/`. Any attempt to escape the directory via `../` triggers an immediate security error.

### 1.3 Memory & Resource DoS Protections
- Maximum page limits (`max_pages: int = 2`) prevent unbounded PDF memory allocations.
- File size bounds on uploaded job descriptions (`100KB` max text length) prevent regex evaluation stalls.

### 1.4 Privacy Classification
- Profiles respect Stage 21's `PrivacyClassification` levels (`public`, `internal`, `confidential`, `restricted`).
- Restricted facts are never embedded in compiled resume documents without explicit cryptographic opt-in.
