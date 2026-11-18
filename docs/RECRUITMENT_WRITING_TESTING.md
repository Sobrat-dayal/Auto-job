# Recruitment Writing Verification & Testing Strategy

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

Stage 24 verification encompasses comprehensive end-to-end automated test suites spanning both the Python FastAPI backend (`services/api/tests/`) and the React desktop frontend (`apps/desktop/src/test/features/`). The testing strategy rigorously validates zero-hallucination fact grounding, sensitive question guards, non-overlapping experience calculation, document rendering, and application packaging.

---

### Backend Test Coverage (`services/api/tests/`)

| Test Suite | File | Focus Areas | Result |
|---|---|---|---|
| **Writing Models** | `test_writing_models.py` | Schema validation for blocks, answers, questions, and packages; enum serialization. | 3 / 3 PASS |
| **Cover Letters** | `test_cover_letters.py` | Block generation, archetypes (`role_specific`, `internship`, etc.), tone/length scaling, DOCX/PDF export. | 5 / 5 PASS |
| **Question Intelligence** | `test_question_intelligence.py` | 16-category classification, input format discovery, raw text parsing. | 2 / 2 PASS |
| **Answer Generation** | `test_answer_generation.py` | Non-overlapping experience calculator, STAR structuring, length limits, fact grounding. | 5 / 5 PASS |
| **Sensitive Decisions** | `test_sensitive_decisions.py` | Work auth, sponsorship, EEO disclosures, legal attestation audit logging, anti-auto-approval guards. | 3 / 3 PASS |
| **Answer Library** | `test_answer_library.py` | Parameter substitution (`{{years_of_experience}}`), leak prevention, freshness lifecycle (`fresh`, `outdated`). | 3 / 3 PASS |
| **Writing Packages** | `test_writing_packages.py` | Immutable package assembly, cryptographic seal (SHA-256), approval state transition. | 2 / 2 PASS |
| **API Endpoints** | `test_api_writing.py` | 27 REST endpoints, auth checks, validation error handling, tenant scoping. | 4 / 4 PASS |
| **Full Regression Suite** | `tests/` | 349 total backend tests across memory, browser, desktop control, profiles, resumes, and writing. | **349 / 349 PASS** |

---

### Desktop Frontend Vitest Suite (`apps/desktop/`)

The desktop test suite (`apps/desktop/src/test/features/recruitment-writing.test.tsx`) simulates authentic user interaction across all 10 workspace tabs:

```
 ✓ renders recruitment writing workspace with overview stats and zero-hallucination badge
 ✓ renders cover letter studio and updates parameters
 ✓ lists existing cover letter drafts and versions
 ✓ renders interactive cover letter editor with block cards
 ✓ displays template gallery with ATS compatibility scores
 ✓ parses questions and displays categorized screening list
 ✓ displays answer library with parameterized templates and freshness badges
 ✓ renders sensitive decisions tab with attestation warnings and confirmation guards
```

- **Execution Time**: ~3.1s
- **Pass Rate**: 8 of 8 tests (100%)
- **TypeScript Typecheck**: `pnpm.cmd -r typecheck` passes with 0 errors across `@autonom/shared`, `@autonom/shared-types`, and `@autonom/desktop`.

---

### Verification Invariants Enforced in Tests

1. **No Ungrounded Claims**: Attempting to generate a cover letter with skills or employers missing from the profile generates `critical` or `error` validation issues.
2. **Strict Sensitive Question Guards**: Calling auto-fill on questions tagged `work_authorization`, `visa_sponsorship`, or `legal_attestation` raises `SensitiveQuestionGuardError` or keeps answers in `requires_user_confirmation`.
3. **No Overlapping Months**: Consecutive or overlapping employment ranges are merged into contiguous disjoint calendar intervals.
4. **Attestation Integrity**: Attestation logs record human actor identity and UTC timestamp; packages cannot be approved if required attestations are unresolved.
5. **Round-Trip Document Extraction**: Exported PDF documents are parsed with `pypdf` to guarantee that text content is 100% extractable and ATS-compatible.
