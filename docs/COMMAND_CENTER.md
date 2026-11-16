# AUTONOM — Command Center Dashboard Specification (Stage 08)

## 1. Overview and Purpose

The **AUTONOM Command Center** is the central operational interface through which the user supervises autonomous AI agents, background task queues, job discovery pipelines, application submissions, desktop automation, and infrastructure health.

AUTONOM is an autonomous assistant where agents perform computer operations, web scraping, and application workflows asynchronously. The user acts as an **executive supervisor and operator**, monitoring progress, approving high-impact actions, and reviewing execution telemetry.

---

## 2. Architecture & Design Principles

### 2.1 Dark Dashboard Palette & Design Tokens

In conformance with the Stage 06 Design System tokens:

- **Base Canvas**: Deep space dark `#0B1220` (`--background`).
- **Surface Elevation**: Layered panel background `#0F1828` (`--surface`), `#121E30` (`--surface-elevated`).
- **Borders & Dividers**: High-contrast subtle borders `#1B2B42` (`--border`).
- **Brand Accents**: Primary Blue `#338BDF` (`--accent-primary`), Precision Cyan `#51C8E8` (`--accent-cyan`).
- **Semantic Badges**: Emerald `#34D399` (Operational/Success), Rose `#F43F5E` (Failed/Error), Amber `#F59E0B` (Warning/Pending), Neutral Slate `#64748B` (Unavailable/Scheduled).

### 2.2 Strict Zero-Fake-Data Integrity Rule

AUTONOM strictly adheres to absolute data honesty:

- **No fabricated metrics**: If 0 jobs are scouted or 0 applications submitted, genuine `0` values are rendered.
- **Roadmap Release Attribution**: Capabilities scheduled for future stages explicitly display roadmap tags and informational explanations:
  - **Job Discovery Crawler**: `Stage 26`
  - **Application Tailor Agent**: `Stage 30`
  - **Autonomous Submissions**: `Stage 31`
  - **Supervisor Swarm Lead**: `Stage 12`
  - **Advance Permissions & Approvals**: `Stage 14`
- **Real SQLite Telemetry**: All task statistics, state counts, durations, and logs reflect actual SQLite records in `%APPDATA%\autonom\autonom.db`.

---

## 3. Command Center Layout Grid

The Command Center dashboard is structured into 7 functional operational tiers:

```
+---------------------------------------------------------------------------------------------------+
| Tier 1: Dashboard Header (System Status, Loopback 8765, Uptime, Dispatch State, Sync Button)      |
+---------------------------------------------------------------------------------------------------+
| Tier 2: Primary KPI Grid (Running Tasks, Queued Tasks, Jobs Discovered [26], Applications [31])   |
|         Secondary Strip (Completed, Failed, Pending Approvals [14], Worker Pool Concurrency)       |
+---------------------------------------------------------------------------------------------------+
| Tier 3: Autonomous Agent Fleet & Worker Pool                                                      |
|   [ Job Discovery (26) ] [ Application Tailor (30) ] [ Swarm Lead (12) ] [ Worker Pool (Real) ]   |
+---------------------------------------------------------------------------------------------------+
| Tier 4: Recruitment & Application Pipeline                                                        |
|   [ Job Discovery Engine (WAL) ]            [ 10-Stage Application Lifecycle Pipeline (WAL) ]     |
+---------------------------------------------------------------------------------------------------+
| Tier 5: Live Execution & Real-Time Event Stream                                                   |
|   [ Live Background Task Queue (Filters/Inspect/Cancel) ]   [ Real-Time SSE Event Stream (Dedupe) ] |
+---------------------------------------------------------------------------------------------------+
| Tier 6: Analytics, System Health & Action Items                                                   |
|   [ Task Trends (Today/7d/30d) ]  [ System Health Breakdown ]  [ Action Items & Operator Gates ]   |
+---------------------------------------------------------------------------------------------------+
| Tier 7: Quick Actions (Dispatch Test Task, Route Shortcuts to Recruitment/Agents/Diagnostics)    |
+---------------------------------------------------------------------------------------------------+
```

---

## 4. Component Details & Operational Flows

### 4.1 Dashboard Header (`DashboardHeader.tsx`)

- Displays application state, API connectivity (`HTTP 127.0.0.1:8765`), backend uptime counter, global dispatch toggle indicator, and roadmap release attribution (`Stage 08 Active`).
- Manual `Sync Dashboard` button initiates synchronous invalidation and refetch across overview metrics, task lists, and trends.

### 4.2 Key Performance Indicators (`DashboardKpiGrid.tsx`)

- **Running Tasks**: Count of tasks currently executing in Python worker threads.
- **Queued Tasks**: Tasks in SQLite queue awaiting worker allocation.
- **Jobs Discovered**: Real count of records from `job_listings` table, badged with `Stage 26`.
- **Applications Submitted**: Real count from `applications` table, badged with `Stage 31`.
- **Secondary Strip**:
  - `Completed Tasks`: Cumulative successful completions.
  - `Failed Tasks`: Tasks that exited with errors, highlighting operator attention.
  - `Pending Approvals`: Advance operator permissions (Stage 14 Gate).
  - `Worker Threads`: Active thread pool capacity (e.g., `0 / 4 active`).

### 4.3 Autonomous Agent Fleet & Worker Pool (`AgentOperationsPanel.tsx`)

- Displays 3 future swarm agents with status `unavailable` and target stage pills (`Stage 26`, `Stage 30`, `Stage 12`).
- Displays 1 distinct active card for the real **Worker Thread Pool** (Stage 03 backend executor), showing thread count, concurrency capacity, and health state.

### 4.4 Recruitment Pipeline (`JobDiscoveryOverview.tsx` & `ApplicationPipeline.tsx`)

- **Job Discovery Overview**: Introspects `job_listings` table. Shows total scouted, scouted today, and active listings. Honest empty state informs user that autonomous scraping begins in Stage 26.
- **10-Stage Application Pipeline**: Visualizes stages:
  1. Discovered
  2. Evaluated
  3. Matched
  4. Queued
  5. Preparing
  6. Submitted
  7. Recruiter Response
  8. Interview
  9. Offer
  10. Closed
- Empty state clearly attributes automated application submissions to Stage 31.

### 4.5 Live Task Execution Queue (`LiveTaskQueue.tsx`)

- Lists active and historical background tasks with real-time status badges, progress bars, creation timestamps, and handler type.
- **Filtering Tabs**: `All Tasks`, `Running`, `Queued`, `Completed`, `Failed`.
- **Cooperative Cancellation**: Immediate trigger to cooperatively terminate running or queued background tasks.
- **Inspection**: Opens accessible modal with full metadata.

### 4.6 Task Execution Detail Modal (`TaskDetailModal.tsx`)

- Radix UI accessible modal.
- Displays full UUID, handler type, execution duration, progress message, error details with code, output payload JSON, and historical SQLite state transitions ledger.

### 4.7 Real-Time Activity Feed (`ActivityFeed.tsx`)

- Connected to FastAPI Server-Sent Events (`GET /api/v1/events/stream`).
- Client-side deduplication using an LRU-style set of event IDs.
- Category filters: `all`, `tasks`, `workers`, `system`.
- Visual streaming pill indicator showing connection health (`LIVE SSE (8765)`).
- Memory-bounded buffer (default 100 entries).

### 4.8 Operational Analytics (`ProductivityChart.tsx`)

- Recharts-based bar chart rendering task completion, failure, and creation trends.
- Window selectors: `Today` (hourly), `7 Days` (daily), `30 Days` (daily).
- Automatically calculates and presents overall success rate percentage and total volume.

### 4.9 Subsystem Health & Operator Gates

- **System Health Panel (`SystemHealthPanel.tsx`)**: Introspects:
  - Backend Sidecar API (FastAPI HTTP 127.0.0.1:8765)
  - Worker Thread Pool (Concurrent task execution engine)
  - SQLite Database & WAL (Storage and schema integrity)
  - Tauri Desktop Supervisor (Native Windows bridge & process manager)
- **Pending Actions Panel (`PendingActionsPanel.tsx`)**:
  - Highlights tasks requiring operator review.
  - Advance authorization notice for Stage 14 permissions.

### 4.10 Quick Operations Bar (`QuickActions.tsx`)

- Instant test task dispatcher (`test.sleep_progress`), enabling manual verification of workers, SSE streaming, and progress bars.
- One-click navigation shortcuts to Recruitment, Applications, Agents, Diagnostics, Desktop Shell, and Storage.
