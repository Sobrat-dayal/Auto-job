# AUTONOM Recruitment Writing Architecture

## Stage 24 of 50 — Recruitment Intelligence Foundation

---

### Executive Overview

The **Recruitment Writing Intelligence Engine** is the core written-communication subsystem within Phase 5 of the AUTONOM 50-stage roadmap. It synthesizes verified facts from Stage 21 (Applicant Profile & Claims), Stage 22 (GitHub Intelligence & Code Attribution), and Stage 23 (ATS-Compatible Resume Intelligence) to generate professional cover letters, parse screening questions, formulate truthful application answers, maintain a reusable approved answer library, and assemble sealed, immutable application packages.

```
       +-----------------------------------------------------------+
       |                  STAGE 21: APPLICANT PROFILE             |
       |  (Verified Identity, Education, Employment, Claims, Skills)|
       +-----------------------------+-----------------------------+
                                     |
       +-----------------------------v-----------------------------+
       |               STAGE 22: GITHUB INTELLIGENCE               |
       |     (Repository Evidence, Language Usage, Commit Proof)   |
       +-----------------------------+-----------------------------+
                                     |
       +-----------------------------v-----------------------------+
       |                STAGE 23: RESUME INTELLIGENCE              |
       |  (ATS Document Model, Role Tailoring, Version Snapshots)  |
       +-----------------------------+-----------------------------+
                                     |
                                     v
+=========================================================================+
|                   STAGE 24: RECRUITMENT WRITING ENGINE                 |
|                                                                         |
|  +--------------------+  +---------------------+  +------------------+  |
|  |    Cover Letter    |  |    Screening Q&A    |  | Sensitive Guards |  |
|  |     Subsystem      |  |     Intelligence    |  |   & Attestation  |  |
|  +---------+----------+  +----------+----------+  +--------+---------+  |
|            |                        |                      |            |
|            +-------------------+    |    +-----------------+            |
|                                |    |    |                              |
|                                v    v    v                              |
|                     +---------------------------+                       |
|                     |  Reusable Answer Library  |                       |
|                     +-------------+-------------+                       |
|                                   |                                     |
|                                   v                                     |
|                     +---------------------------+                       |
|                     | Application Writing Pack  |                       |
|                     | (Sealed, SHA-256 Digest)  |                       |
|                     +---------------------------+                       |
+=========================================================================+
```

---

### Architectural Pillars

1. **Zero-Hallucination Mandate**
   - Every substantive claim, metric, employment duration, credential, and skill must originate from verified canonical facts.
   - When required facts are missing, the engine records an explicit `missing_information` state rather than inventing plausible qualifications.
   - Ambiguities generate `conflicting_information` flags for human review.

2. **Strict Sensitive Decision Guards**
   - Work authorization, visa sponsorship, disability disclosures, race/ethnicity self-identification, veteran status, and legal attestations are classified under sensitive protection guards.
   - The engine **NEVER** auto-approves or silently auto-answers protected questions.
   - Requires explicit human choice (`requires_user_confirmation`) or signed attestation (`requires_user_attestation`).

3. **Multi-Archetype Cover Letter Architecture**
   - Distinct structural archetypes: `role_specific`, `experienced`, `internship`, `research`, `short`, and `general`.
   - Block-based modular structure: `header`, `salutation`, `opening`, `qualifications`, `evidence_example`, `motivation`, `closing`, and `signature`.
   - Export pipelines supporting DOCX (via `python-docx`) and PDF (via `reportlab` with `pypdf` text extraction verification).

4. **16-Category Screening Question Engine**
   - Classifies free-form job screening questions into 16 discrete categories (e.g. `work_authorization`, `compensation`, `experience_years`, `technical_knowledge`, `behavioral_star`, etc.).
   - Discovers expected answer types: `free_text`, `short_text`, `numeric`, `boolean_yes_no`, `single_choice`, `dropdown`, etc.
   - Evaluates non-overlapping professional tenure, calculating genuine verified experience years.

5. **Reusable Answer Library & Freshness Monitoring**
   - Houses parameterized templates (e.g. `{{years_of_experience}}`, `{{primary_tech_stack}}`) for approved responses.
   - Automatically monitors freshness status: flags answers as `outdated` or `requires_revalidation` when the canonical applicant profile changes.
   - Employs strict leak prevention: sanitizes company names, proprietary internal tools, and job IDs before previewing or transferring answers.

6. **Immutable Application Writing Packages**
   - Aggregates target job context, profile snapshot, resume snapshot, cover letter version, and all screening Q&As.
   - Computes cryptographic SHA-256 digests over all package components.
   - Enforces approval gates before package finalization.

---

### Directory Layout & Component Responsibilities

```
services/api/app/recruitment/writing/
├── __init__.py                 # Module exports
├── contracts.py                # Domain Enums, Pydantic DTOs, and schema contracts
├── errors.py                   # Domain-specific hierarchy of WritingEngineError
├── templates.py                # 6 Professional Cover Letter Design Templates
├── block_generator.py          # Modular block generation and STAR structuring
├── validator.py                # Zero-hallucination fact validator & evidence auditor
├── versions.py                 # Version snapshots, content hashing, and diff manager
├── exports.py                  # DOCX and PDF export engines with round-trip extraction
├── question_classifier.py      # 16-category classifier and input format detector
├── experience_calculator.py    # Non-overlapping tenure and duration aggregator
├── fact_resolver.py            # Profile claim, project, and GitHub evidence resolver
├── answer_generator.py         # Grounded answer generation and length limiter
├── sensitive_guards.py         # EEO, sponsorship, and attestation protection policies
├── answer_library.py           # Parameterized template repository & freshness watcher
├── package_manager.py          # Application package lifecycle and cryptographic seal
├── agent_adapter.py            # Recruitment agent snapshot and query provider
└── service.py                  # Central RecruitmentWritingService orchestrator
```

---

### Security and Isolation Boundaries

- **Local Storage**: All draft letters, answers, and packages are maintained within the user's isolated local SQLite database (`autonom.db`) and artifacts directory.
- **Tenant Isolation**: All operations are bounded by `owner_id` derived directly from authenticated security tokens (`AuthContext`).
- **No External Exfiltration**: Recruitment writing does not perform automated external submissions or recruiter emails, adhering strictly to Stage 24 boundaries.
