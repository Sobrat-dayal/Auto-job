# Job Watches Specification (Stage 30)

## 1. Overview
A **Job Watch** represents a durable, authorized monitoring target configured to discover, aggregate, and evaluate job vacancies over time.

## 2. Watch Lifecycle State Machine
```
   [DRAFT] --------> [VALIDATING] --------> [ACTIVE] <--------> [PAUSED]
      |                                        |
      |                                        v
   [ARCHIVED]                             [SUSPENDED] (e.g. repeated errors)
                                               |
                                               v
                                         [RATE_LIMITED] (provider cooldown)
```

### State Definitions
- **`draft`**: Incomplete watch configuration undergoing initial authoring.
- **`validating`**: Syntactic and filter sanity checks in progress.
- **`active`**: Eligible for scheduled execution runs.
- **`paused`**: Temporarily halted by user action; execution timers suspended.
- **`suspended`**: Halted automatically due to successive unexpected errors ($N \ge 3$).
- **`rate_limited`**: Temporarily frozen awaiting provider rate limit reset (`retry-after`).
- **`disabled`**: Explicitly shut down due to policy or credential revocation.
- **`archived`**: Retained for audit and telemetry history; non-executable.

## 3. Configuration Contract
Each Job Watch includes:
- `profile_id`: Target monitoring profile.
- `watch_type`: `career_strategy`, `employer_list`, `role_search`, or `custom_source`.
- `career_strategy_id`: Associated career preferences and hard policies (Stage 25).
- `approved_sources`: Platform source IDs (e.g., `greenhouse_public`, `lever_published`).
- `employer_ids`: Specific employer companies to monitor.
- `role_filters` & `location_filters`: Domain and geographic constraints.
- `schedule_config`: Timezone, interval, quiet hours, and missed run policies.
- `alert_rules`: Notification threshold configuration.
