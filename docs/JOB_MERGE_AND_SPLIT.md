# Transactional Job Merge & Split Operations (Stage 27)

## Overview
AUTONOM supports atomic, transactional merges of canonical vacancies as well as safe separation (split/unmerge) to reverse erroneous merges without data loss.

## Atomic Merge Protocol (`MergeExecutionEngine`)
1. **Pre-flight Validation & Cycle Prevention**:
   - Asserts `surviving_job_id != superseded_job_id`.
   - Resolves existing aliases via `SupersessionManager` to prevent circular redirects ($A \to B \to A$).
2. **Source Link Transfer**:
   - Reassigns foreign keys in `canonical_job_source_links` from `superseded_job_id` to `surviving_job_id`.
3. **Location Transfer**:
   - Transfers office records in `canonical_job_locations` to surviving job.
4. **Alias Creation**:
   - Inserts record into `canonical_job_aliases`: `superseded_id` $\to$ `surviving_id`.
5. **State Updates**:
   - Marks superseded job as `status = 'closed'`, `identity_status = 'rejected'`.
   - Increments surviving job's `source_count` and `version`.
6. **Audit & Snapshot**:
   - Records operation in `job_merge_operations`.
   - Appends snapshot in `canonical_job_versions`.

## Atomic Split Protocol (`SplitExecutionEngine`)
1. **Validation**:
   - Ensures at least one source link remains on the original job (cannot split away all sources).
2. **New Entity Generation**:
   - Creates a new canonical job identity with title and employer replicated from detached sources.
3. **Source Reassignment**:
   - Reassigns specified source link IDs to the newly created canonical job.
4. **Version Increment & Audit**:
   - Decrements original job's `source_count` and increments its `version`.
   - Sets new job's `source_count` and initializes its version history.
   - Records operation in `job_split_operations`.
