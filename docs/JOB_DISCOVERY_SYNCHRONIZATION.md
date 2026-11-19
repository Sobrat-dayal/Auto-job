# Job Discovery Synchronization and Invariant Safety (Stage 26)

## Incremental Synchronization Protocol
AUTONOM synchronizes with job sources incrementally to avoid redundant data transfer and respect provider infrastructure:
1. **Conditional Fetching**: Uses HTTP `ETag` (`If-None-Match`) and `Last-Modified` (`If-Modified-Since`) stored in `HttpCacheManager`.
2. **Change Detection**: When listings are retrieved, the coordinator compares them against existing observations:
   - **New**: Posting ID observed for the first time -> `new_count++`.
   - **Updated**: Existing posting with modified title, description, or compensation -> `updated_count++`.
   - **Unchanged**: Posting unchanged -> `unchanged_count++`.
   - **Closed**: Posting absent from a verified complete snapshot -> `closed_count++`.

## CRITICAL SAFETY INVARIANT: Partial Snapshots Never Close Postings
```
┌────────────────────────────────────────────────────────────────────────┐
│                          CRITICAL INVARIANT                            │
│  Partial, interrupted, or rate-limited snapshots MUST NEVER mark       │
│  absent postings as closed or removed!                                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Problem Statement
If an API client encounters an HTTP 429 rate limit, network timeout, or server error on page 3 of 10, an unverified synchronizer might falsely assume that postings from pages 4–10 have been filled and close hundreds of active vacancies.

### AUTONOM's Formal Enforcement
Every synchronization produces a `JobSourceSnapshot` categorized by `SnapshotCompleteness`:
- `COMPLETE`: 100% of pages/items were fetched without interruption.
- `PARTIAL`: Network error or timeout occurred mid-fetch.
- `RATE_LIMITED`: Provider returned HTTP 429.
- `FAILED`: Fatal failure before retrieving listings.

In `DiscoveryCoordinator.sync_source`:
```python
if snapshot.completeness == SnapshotCompleteness.COMPLETE:
    # Only close postings absent from verified complete snapshots
    for (s_id, n_id), obs_id in self._source_posting_index.items():
        if s_id == source_id and n_id not in observed_native_ids:
            obs.availability = PostingAvailability.CLOSED
            snapshot.closed_count += 1
else:
    # PRESERVE all existing observations in their current state
    logger.info("Preserving existing active postings without closing")
```
