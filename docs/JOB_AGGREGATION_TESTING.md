# Job Aggregation Testing & QA Verification Suite (Stage 27)

## Overview
Stage 27 is verified by an exhaustive, multi-tier testing suite covering backend normalization, employer resolution, similarity scoring, transactional merge/split operations, idempotency, FastAPI REST endpoints, and React frontend components.

## Test Matrix

### 1. Multi-Source Ingestion & Duplicate Rules
- **File**: `services/api/tests/test_job_aggregation_multi_source.py` (3 tests)
  - `test_same_job_multiple_sources`: Ingests identical vacancy across Greenhouse, Lever, and Feed; asserts single canonical job is created with `source_count == 3` and correct links.
  - `test_same_title_different_jobs`: Ingests roles with identical titles but different requisition IDs under the same company; asserts separate canonical jobs are created (Negative Evidence test).
  - `test_different_employers_not_merged`: Ingests identical job titles across Stripe vs Square; asserts entities are never merged.

### 2. Employer Identity & Aliases
- **File**: `services/api/tests/test_employer_identity_and_aliases.py` (3 tests)
  - `test_employer_alias_resolution`: Tests normalization of corporate suffixes (`Stripe, Inc.` $\to$ `Stripe`).
  - `test_staffing_agency_classification`: Tests classification of recruiting firms (`Robert Half`) as `OrganizationType.STAFFING_AGENCY`.
  - `test_career_policy_blocklist_integration`: Tests rejection and filtering of Stage 25 blocklisted employers.

### 3. Multi-Location & Reposts
- **File**: `services/api/tests/test_multi_location_and_reposts.py` (3 tests)
  - `test_multi_location_same_requisition`: Tests same requisition listed across London and New York; asserts single canonical job with multiple office location entries.
  - `test_repost_detection`: Tests vacancy posted 90 days after closing; verifies repost flag and new version history.
  - `test_evergreen_posting_updates`: Tests continuously refreshed evergreen postings.

### 4. Field Conflicts & Source Reconciliation
- **File**: `services/api/tests/test_field_conflicts_and_reconciliation.py` (2 tests)
  - `test_field_conflict_logging`: Tests conflicting salary ranges logged to `canonical_job_conflicts` and manual resolution.
  - `test_source_authority_ranking`: Tests preferred field value selection according to source authority weights.

### 5. Transactional Merge & Split Operations
- **File**: `services/api/tests/test_merge_and_split_operations.py` (2 tests)
  - `test_merge_preview_and_execution`: Tests merge preview, execution, source link transfer, alias creation, and alias resolution.
  - `test_false_merge_and_split`: Tests reversing an erroneous merge by detaching source links into a newly created canonical entity.

### 6. Idempotency, Status, & Checkpointing
- **File**: `services/api/tests/test_idempotency_and_partial_snapshots.py` (3 tests)
  - `test_idempotent_ingestion`: Repeatedly processes identical observation; verifies single canonical entity with no version explosion.
  - `test_partial_snapshot_status_reconciliation`: Verifies missing items from partial feeds are marked `POSSIBLY_ACTIVE` rather than `CLOSED`.
  - `test_batch_checkpointing_workflow`: Verifies incremental batch checkpoint persistence.

### 7. FastAPI REST API Integration
- **File**: `services/api/tests/test_api_job_aggregation.py` (5 tests)
  - `test_api_aggregation_unauthorized`: Verifies 401 on unauthenticated access.
  - `test_api_aggregation_overview_and_diagnostics`: Verifies 200 OK on status and diagnostics endpoints.
  - `test_api_process_single_and_batch_observation`: Tests `/process`, `/process-batch`, `/jobs/{id}`, `/sources`, `/history`.
  - `test_api_employers_and_resolution`: Tests `/employers`, `/employers/{id}`, `/employers/resolve`.
  - `test_api_duplicates_and_settings`: Tests `/duplicates`, `/conflicts`, `/settings` (GET and PUT).

### 8. React Desktop Vitest Suite
- **File**: `apps/desktop/src/test/JobAggregationWorkspace.test.tsx` (4 tests)
  - Workspace header and telemetry render.
  - All 8 navigation tabs render.
  - Tab navigation to Employers tab and Interactive Identity Resolver.
  - Tab navigation to Merge & Split Ops tab.

## Execution Summary
- **Backend Pytest**: **21 / 21 tests passed (100%)**
- **Frontend Vitest**: **4 / 4 workspace tests passed (100%)**, **5 / 5 App.test.tsx passed (100%)**
- **TypeScript Typecheck**: **0 errors (`tsc --noEmit` exited with code 0)**
