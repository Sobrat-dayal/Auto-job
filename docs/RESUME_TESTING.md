# AUTONOM — Resume Testing & Verification Strategy (Stage 23)

## 1. Quality Assurance & Test Architecture

The Resume Intelligence subsystem is covered by an exhaustive end-to-end test suite spanning backend unit tests, domain integration tests, REST API tests, and frontend UI component tests.

```
+-------------------------------------------------------------+
|                     Test Suites Overview                    |
+-------------------------------------------------------------+
| Backend Pytest Suite:                                       |
| - test_resume_ats.py (2 tests)                             |
| - test_resume_content.py (6 tests)                         |
| - test_resume_models.py (3 tests)                          |
| - test_resume_renderers.py (3 tests)                        |
| - test_resume_tailoring.py (3 tests)                        |
| - test_resume_versioning_and_portfolio.py (3 tests)        |
| - test_api_resumes.py (4 tests)                            |
| Total: 24 tests (100% Pass Rate)                           |
+-------------------------------------------------------------+
| Frontend Vitest Suite:                                      |
| - resume-portfolio.test.tsx (8 tests)                       |
| Total: 8 tests (100% Pass Rate)                             |
+-------------------------------------------------------------+
| Monorepo TypeScript Build:                                  |
| - @autonom/shared: 0 errors                                 |
| - @autonom/shared-types: 0 errors                           |
| - @autonom/desktop: 0 errors                                |
+-------------------------------------------------------------+
```

---

## 2. Test Cases & Verification Details

### 2.1 Content Verification (`test_resume_content.py`)
- Verifies deterministic generation of professional summaries.
- Validates categorization of flat technical skill lists into domain groups.
- Confirms `ExperienceBulletEngine` transforms raw achievements into active-verb bullet points.
- Proves `ContentValidatorEngine` detects and rejects ungrounded/hallucinated skill tokens.

### 2.2 Native Renderers & Round-Trip Extraction (`test_resume_renderers.py`)
- Verifies `DocxResumeRenderer` emits valid Word `.docx` binaries with correct OpenXML section headers and bullet lists.
- Verifies `PdfResumeRenderer` emits valid PDF binaries with correct ReportLab flowable sequences.
- Confirms `DocumentRoundTripValidator` successfully extracts text using `pypdf` and validates candidate name, contact coordinates, and section titles.

### 2.3 Job Tailoring (`test_resume_tailoring.py`)
- Tests parsing of raw job postings into required skills, preferred skills, and experience constraints.
- Tests `EvidenceMatchingEngine` classification into `Directly Supported`, `Partially Supported`, `Related Domain`, and `Not Evidenced`.
- Guarantees that missing skills are honestly flagged as gaps rather than invented.

### 2.4 Versioning & Portfolio (`test_resume_versioning_and_portfolio.py`)
- Tests approval of drafts, incrementing version numbers, and computing canonical SHA-256 digests.
- Tests portfolio creation, demonstrated project tracking, and privacy stripping of private repository links.
- Confirms multi-page PDF dossier and standalone HTML export.

### 2.5 REST API Endpoints (`test_api_resumes.py`)
- Validates full HTTP CRUD lifecycle over `/api/v1/resumes`, `/api/v1/job-descriptions/analyze`, `/api/v1/resumes/{id}/tailor`, `/api/v1/resumes/{id}/ats-report`, `/api/v1/resumes/{id}/approve`, `/api/v1/resumes/{id}/export`, and `/api/v1/portfolios`.
