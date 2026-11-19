# Recruitment Monitoring Observability & Metrics (Stage 30)

## 1. Key Performance Indicators (KPIs)
The monitoring engine computes real-time operational metrics across:
- **`monitoring_enabled`**: Boolean state of background dispatching.
- **`active_watches_count`**: Number of watches in `active` status.
- **`total_opportunities_count`**: Total vacancies indexed in the opportunity queue.
- **`high_priority_count`**: Opportunities evaluated with priority `high`.
- **`ready_for_preparation_count`**: Opportunities satisfying Stage 31 readiness prerequisites.
- **`unread_alerts_count`**: Unread alert notifications.
- **`next_scheduled_run_at`**: Soonest scheduled watch execution timestamp.
- **`last_successful_run_at`**: Timestamp of the most recent completed run.

## 2. Health Monitoring & Heartbeats
Heartbeats are maintained and verified for key system components:
- `recruitment_scheduler`
- `monitoring_workers`
- `discovery_agent`
- `intelligence_agent`
- `matching_agent`

Component states report `healthy`, `degraded`, or `down` via `/api/v1/recruitment-monitoring/diagnostics`.
