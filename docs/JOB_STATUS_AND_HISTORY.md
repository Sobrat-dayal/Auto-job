# Job Posting Status Reconciliation & Version History (Stage 27)

## Overview
Tracking whether a job vacancy remains active or has closed requires conservative rules that prevent false closures caused by incomplete discovery snapshots or intermittent network timeouts.

## Conservative Status Reconciliation Rules (`reconcile_canonical_status`)

1. **Active Rule**:
   - If *at least one* authoritative source confirms the posting is currently available, its canonical status is `ACTIVE`.
2. **Partial Snapshot Non-Closure Invariant**:
   - If a source sync was partial, rate limited, or interrupted, missing postings CANNOT be marked closed. They transition to `POSSIBLY_ACTIVE` pending complete verification.
3. **Closure Rule**:
   - Only when *all* observed authoritative sources explicitly confirm closure (`closed`, `expired`, `removed`) is the canonical posting transitioned to `CLOSED`.

## Immutable Version History (`canonical_job_versions`)
Whenever a canonical job undergoes meaningful structural change, an immutable snapshot is recorded:
- `canonical_job_id`: Target job ID.
- `version_number`: Incremented integer revision.
- `snapshot_json`: Full attribute snapshot at revision time.
- `change_summary`: Human-readable explanation (e.g. `Merged duplicate job cjob_2: Authorized duplicate merge`).
- `created_at`: UTC timestamp.
