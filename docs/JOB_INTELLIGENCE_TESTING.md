# Job Intelligence Testing & Verification (Stage 28)

## 1. Overview
The Job Requirement Intelligence Engine is backed by an automated testing suite comprising 16 backend pytest suites (35 unit and integration tests) and 1 frontend Vitest integration suite (5 tests).

## 2. Test Matrix

| Test Suite File | Focus Area | Assertions & Invariants Verified |
|---|---|---|
| `test_requirement_classification.py` | Mandatory vs Preferred | Preferred items never promoted; responsibilities not gating |
| `test_requirement_logic.py` | Logical Relationships | AND, OR, AtLeastN, EquivalentAlternative detection |
| `test_negation_parsing.py` | Scoped Negation | "AWS not required", "No prior experience", "Sponsorship unavailable" |
| `test_education_extraction.py` | Degree Requirements | Degree levels, fields of study, practical equivalencies |
| `test_experience_extraction.py` | Tenure Durations | Min/max years, 5+ years, 3-5 years, domain categories |
| `test_compensation_intelligence.py` | Compensation | Ranges with em-dash, hourly/annual, zero synthetic guessing |
| `test_remote_eligibility.py` | Employment Conditions | Remote (US only), Hybrid office days, travel percentages |
| `test_work_authorization_extraction.py` | Work Authorization | Work auth required, visa sponsorship offered/refused, citizenship |
| `test_deadline_intelligence.py` | Deadlines & Instructions | Closing dates, rolling status, required document checklists |
| `test_source_conflicts.py` | Multi-Source Conflicts | Detects contradictions between disparate source descriptions |
| `test_ai_hallucination_defense.py` | Hallucination Defense | Verifies every supporting quote exists verbatim in source text |
| `test_prompt_injection_safety.py` | Security Sanitization | Defuses adversarial prompt injections into safe placeholder |
| `test_multi_agent_analysis.py` | Agent Capabilities | Verifies typed callable capability contracts |
| `test_source_update_versioning.py` | Versioning | SHA-256 description hashing and reanalysis triggers |
| `test_analysis_without_ai.py` | Offline Fallback | Full end-to-end extraction without AI availability |
| `test_api_job_intelligence.py` | REST API Endpoints | Authenticated endpoint execution, CRUD, review resolution |
| `job-intelligence.test.tsx` (Vitest) | Desktop Workspace UI | Header, KPIs, analyzed jobs table, requirements explorer, review queue |

## 3. Execution Commands
```bash
# Run backend pytest suite
pytest services/api/tests/test_requirement_classification.py \
       services/api/tests/test_requirement_logic.py \
       services/api/tests/test_negation_parsing.py \
       services/api/tests/test_education_extraction.py \
       services/api/tests/test_experience_extraction.py \
       services/api/tests/test_compensation_intelligence.py \
       services/api/tests/test_remote_eligibility.py \
       services/api/tests/test_work_authorization_extraction.py \
       services/api/tests/test_deadline_intelligence.py \
       services/api/tests/test_source_conflicts.py \
       services/api/tests/test_ai_hallucination_defense.py \
       services/api/tests/test_prompt_injection_safety.py \
       services/api/tests/test_multi_agent_analysis.py \
       services/api/tests/test_source_update_versioning.py \
       services/api/tests/test_analysis_without_ai.py \
       services/api/tests/test_api_job_intelligence.py

# Run frontend Vitest suite
pnpm --filter @autonom/desktop test job-intelligence --run
```
