# AUTONOM — Dashboard Metrics & Calculations (Stage 08)

## 1. Principles of Operational Metrics

AUTONOM follows a strict **zero-fabrication policy**. Operational analytics reflect real system state, durable SQLite records, and actual thread pool status.

When capabilities belong to future development stages, they are explicitly attributed to their respective roadmap release rather than mocked with synthetic counters.

---

## 2. Metric Catalog & Definitions

### 2.1 Task Execution Metrics

Aggregated live from `services/api/app/services/task_execution_manager.py` (in-memory state) and verified against `services/api/app/db/repositories/task_repository.py` (SQLite `tasks` table).

| Metric              | Source         | Type       | Calculation / Formula                                               |
| :------------------ | :------------- | :--------- | :------------------------------------------------------------------ |
| **Running Tasks**   | Memory + DB    | Gauge      | In-memory active tasks where `state == 'running'`.                  |
| **Queued Tasks**    | Memory + DB    | Gauge      | In-memory tasks in state `queued` or `planning` awaiting execution. |
| **Completed Tasks** | SQLite `tasks` | Cumulative | Count of rows where `state == 'completed'`.                         |
| **Failed Tasks**    | SQLite `tasks` | Cumulative | Count of rows where `state == 'failed'`.                            |
| **Cancelled Tasks** | SQLite `tasks` | Cumulative | Count of rows where `state == 'cancelled'`.                         |
| **Total Tasks**     | SQLite `tasks` | Cumulative | Total rows in `tasks` table.                                        |

---

### 2.2 Worker Pool Metrics

Aggregated from `services/api/app/services/worker_manager.py`.

| Metric             | Source         | Type    | Description                                                                            |
| :----------------- | :------------- | :------ | :------------------------------------------------------------------------------------- |
| **Active Workers** | Worker Manager | Gauge   | Number of Python worker threads currently executing a task (`worker.is_busy == True`). |
| **Total Workers**  | Configuration  | Static  | Configured concurrency pool (default: 4 concurrent threads).                           |
| **Idle Workers**   | Calculation    | Derived | `total_workers - active_workers`.                                                      |
| **Worker State**   | Memory         | State   | `READY` if workers alive, `DEGRADED` if thread error, `OFFLINE` if stopped.            |

---

### 2.3 Recruitment & Pipeline Metrics

Aggregated from SQLite tables `job_listings` and `applications`.

| Metric                     | Source         | Initial Stage | Description                                                                                                                                                             |
| :------------------------- | :------------- | :------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Jobs Discovered**        | `job_listings` | Stage 26      | Count of rows in `job_listings`. Displays `0` until Stage 26 scrapers activate.                                                                                         |
| **Discovered Today**       | `job_listings` | Stage 26      | Rows in `job_listings` where `created_at >= start_of_today`.                                                                                                            |
| **Active Listings**        | `job_listings` | Stage 26      | Rows where `status == 'active'` or `is_expired == 0`.                                                                                                                   |
| **Applications Total**     | `applications` | Stage 31      | Count of rows in `applications`. Displays `0` until Stage 31 engine activates.                                                                                          |
| **Applications Submitted** | `applications` | Stage 31      | Rows where `stage == 'submitted'`.                                                                                                                                      |
| **10 Pipeline Stages**     | `applications` | Stage 31      | Histogram of applications per stage (`discovered`, `evaluated`, `matched`, `queued`, `preparing`, `submitted`, `recruiter_response`, `interview`, `offer`, `rejected`). |

---

### 2.4 Time-Windowed Task Execution Trends

Calculated in `services/api/app/api/v1/endpoints/dashboard.py` via `_compute_task_trends()`.

#### Windows

1. **Today (`today`)**:
   - Time window: Last 24 hours.
   - Bucketing: 1-hour intervals (`HH:00`).
2. **7 Days (`7d`)**:
   - Time window: Last 7 calendar days.
   - Bucketing: 1-day intervals (`YYYY-MM-DD`).
3. **30 Days (`30d`)**:
   - Time window: Last 30 calendar days.
   - Bucketing: 1-day intervals (`YYYY-MM-DD`).

#### Derived Aggregates

- **Total Volume**: `sum(datapoint.created for datapoint in data_points)`.
- **Overall Success Rate**:
  $$\text{Success Rate} = \frac{\sum \text{Completed}}{\sum \text{Completed} + \sum \text{Failed}} \times 100\%$$
  _(Returns `100.0%` if both Completed and Failed are `0`)._
