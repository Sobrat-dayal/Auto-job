# Monitoring Pipeline Orchestration (Stage 30)

## 1. Master Pipeline Flow
The `MonitoringRunCoordinator` executes an end-to-end multi-stage pipeline:

```
[1. Lock & Budget] -> [2. Source Fetching] -> [3. Canonical Aggregation] -> [4. Change Detection]
        |                                                                           |
        v                                                                           v
[8. Alerts Outbox] <-- [7. Opportunity Queue] <-- [6. Policy & Matching] <-- [5. Requirements]
```

### Execution Phases
1. **Safety Pre-Check**: Confirms emergency stop is inactive and acquires atomic task lease.
2. **Phase 1: Discovering**: Fetches public postings from authorized sources without scraping or bypassing authentication.
3. **Phase 2: Aggregating**: Resolves employer identity and canonical vacancy duplicates (Stage 27).
4. **Phase 3: Detecting Changes**: Compares new observation snapshots against stored records.
5. **Phase 4: Analyzing Requirements**: Triggers Stage 28 intelligence if material description updates occurred.
6. **Phase 5: Recalculating Matches**: Updates Stage 29 explainable relevance and eligibility scores.
7. **Phase 6: Updating Queue**: Recalculates opportunity priority and generates Stage 31 readiness contract.
8. **Phase 7: Generating Alerts**: Emits deduplicated alert events and stages notification outbox entries.
9. **Finalization**: Records progress metrics, releases worker lease, and sets `next_due_run_at`.
