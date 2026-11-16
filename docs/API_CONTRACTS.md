# AUTONOM — API Contracts & Inter-Process Specifications

This document defines the formal API contracts between the Tauri desktop client, the React frontend, and the Python FastAPI agent backend service.

---

## 1. REST Endpoints (Python FastAPI Service)

The Python backend listens on `http://127.0.0.1:8765` by default (configurable via `AUTONOM_PORT`).

### 1.1 Core System & Health Endpoints (API v1)

> _Routing Note_: Canonical endpoints are versioned under `/api/v1/*`. `/api/health` aliases to `/api/v1/health`.

#### `GET /api/v1/health` (or `/api/health`)

Returns actual service health, uptime, environment, and loopback enforcement status.

- **Request**: None
- **Response Model**: `HealthResponse`

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 45.2,
  "timestamp": "2026-11-16T07:45:00.000Z",
  "environment": "development",
  "is_loopback": true
}
```

#### `GET /api/v1/ready`

Returns whether the API service is fully initialized and ready to receive requests.

- **Request**: None
- **Response Model**: `ReadinessResponse`

```json
{
  "ready": true,
  "status": "ready",
  "checks": {
    "api_router": true,
    "config_loaded": true,
    "data_dir_accessible": true
  },
  "timestamp": "2026-11-16T07:45:00.000Z"
}
```

#### `GET /api/v1/version`

Returns formal application version, API version prefix, runtime Python version, and host OS platform.

- **Request**: None
- **Response Model**: `VersionResponse`

```json
{
  "app_name": "AUTONOM API",
  "version": "0.1.0",
  "api_version": "v1",
  "python_version": "3.12.13",
  "platform": "win32"
}
```

#### `GET /api/system`

Returns real-time hardware telemetry and OS metrics.

- **Request**: None
- **Response**:

```json
{
  "os": "Windows 11",
  "platform": "win32",
  "python_version": "3.11.15",
  "cpu_usage_percent": 12.4,
  "memory": {
    "total_mb": 32678,
    "available_mb": 18450,
    "process_rss_mb": 84.2
  },
  "monitors": [
    {
      "index": 0,
      "width": 1920,
      "height": 1080,
      "scale_factor": 1.0,
      "is_primary": true
    }
  ]
}
```

### 1.2 Task Execution & Worker Management (Stage 03)

#### `GET /api/v1/system/status`

Returns real-time backend service status, worker pool utilization, task queue counts, and uptime.

#### `GET /api/v1/system/capabilities`

Returns supported task handler types (`compute.echo`, `test.sleep_progress`), concurrency bounds, and queue capacities.

#### `GET /api/v1/workers`

Returns real-time status of all asynchronous worker coroutines, including active tasks and processed task totals.

#### `POST /api/v1/tasks`

Creates and enqueues a new background task for execution.

- **Request**: `TaskCreateRequest` (`task_type`, `payload`, `priority`, `timeout_seconds`, `correlation_id`)
- **Response**: `TaskResponse` (`task_id`, `state`, `progress`, `created_at`)

#### `GET /api/v1/tasks`

Lists all active and recently executed tasks.

#### `GET /api/v1/tasks/{task_id}`

Returns the current execution state and progress of a specific task.

#### `GET /api/v1/tasks/{task_id}/result`

Returns the final output or error for a completed, failed, or cancelled task.

#### `POST /api/v1/tasks/{task_id}/cancel`

Requests cooperative cancellation of a queued or running task.

#### `GET /api/v1/events/stream`

Server-Sent Events (SSE) streaming endpoint delivering live system, worker, and task events.

#### `GET /api/v1/events/recent`

Returns diagnostic event history from the in-memory ring buffer (up to 200 events).

### 1.3 Agent Swarm Management

#### `GET /api/agents`

Returns the status of all registered agents in the swarm.

- **Request**: None
- **Response**:

```json
{
  "agents": [
    {
      "id": "coordinator-01",
      "name": "Lead Coordinator",
      "role": "Orchestrator",
      "status": "idle",
      "current_task": null,
      "tasks_completed": 0,
      "model": "gpt-4o"
    },
    {
      "id": "scout-01",
      "name": "Job Scout",
      "role": "Discovery",
      "status": "idle",
      "current_task": null,
      "tasks_completed": 0,
      "model": "gpt-4o-mini"
    },
    {
      "id": "tailor-01",
      "name": "Resume Tailor",
      "role": "Document Generation",
      "status": "idle",
      "current_task": null,
      "tasks_completed": 0,
      "model": "claude-3-5-sonnet"
    },
    {
      "id": "submitter-01",
      "name": "Application Submitter",
      "role": "Computer Interaction",
      "status": "idle",
      "current_task": null,
      "tasks_completed": 0,
      "model": "claude-3-5-sonnet"
    }
  ],
  "total_active_tasks": 0
}
```

#### `POST /api/agents/{agent_id}/dispatch`

Dispatches a new task to an agent.

- **Request**:

```json
{
  "task_type": "job_search",
  "parameters": {
    "keywords": ["Principal Software Engineer", "Full Stack"],
    "location": "Remote",
    "min_salary": 180000
  },
  "priority": "normal"
}
```

- **Response**:

```json
{
  "task_id": "tsk_018f92a3",
  "status": "queued",
  "assigned_agent": "scout-01",
  "created_at": "2026-11-16T07:30:00Z"
}
```

### 1.3 Job Management

#### `GET /api/jobs`

Retrieves aggregated job postings with pagination and filters.

- **Parameters**: `query` (string), `platform` (string), `min_match` (float), `limit` (int), `offset` (int)
- **Response**:

```json
{
  "total": 0,
  "jobs": [],
  "page": 1,
  "limit": 20
}
```

### 1.4 Autonomy Governance

#### `GET /api/governance/approvals`

Lists pending human-in-the-loop approvals.

- **Response**:

```json
{
  "pending_approvals": []
}
```

#### `POST /api/governance/approvals/{approval_id}`

Submits user decision for a pending approval.

- **Request**:

```json
{
  "decision": "approved",
  "comments": "Proceed with Greenhouse submission",
  "advance_grant_hours": 0
}
```

### 1.5 Storage, Settings & Secure Credentials (Stage 04)

#### `GET /api/v1/storage/status`

Returns database file size, WAL size, artifacts size, backup counts, and free disk space.

- **Auth**: Required
- **Response**: `StorageStatus`

#### `GET /api/v1/storage/health`

Executes SQLite `PRAGMA integrity_check` and `PRAGMA foreign_key_check`.

- **Auth**: Required
- **Response**: `StorageHealth`

#### `POST /api/v1/storage/backups`

Creates an online atomic snapshot using SQLite backup API and generates SHA-256 manifest.

- **Auth**: Required
- **Response**: `BackupManifest` (201 Created)

#### `GET /api/v1/storage/backups`

Returns all available database backups, newest first.

- **Auth**: Required
- **Response**: `BackupManifest[]`

#### `POST /api/v1/storage/restore`

Restores database from specified backup with pre-restore safety snapshot and post-restore integrity check.

- **Auth**: Required
- **Request**: `{"filename": "backup_*.db", "confirm": true}`
- **Response**: `RestoreResponse`

#### `GET /api/v1/tasks/{task_id}/history`

Returns durable event history for a task from the SQLite `task_events` audit table.

- **Auth**: Required
- **Response**: `TaskEventRecord[]`

#### `GET /api/v1/settings` & `PATCH /api/v1/settings/{key}`

Retrieves and updates application settings.

- **Auth**: Required

#### `POST /api/v1/profiles` & `GET /api/v1/profiles`

Creates applicant profile with encrypted contact info (DPAPI) and lists profiles.

- **Auth**: Required

#### `GET /api/v1/integrations/credentials/status`

Lists configured credential providers with secrets masked (`is_configured: true`).

- **Auth**: Required

#### `POST /api/v1/integrations/credentials`

Stores integration credential encrypted at rest via DPAPI and AES-256-GCM.

- **Auth**: Required

---

## 2. Real-Time WebSocket Streaming (`/ws/events`)

The frontend establishes a persistent WebSocket connection to receive real-time telemetry, agent thinking steps, and notifications.

### 2.1 Event Schema

Every event sent across `/ws/events` adheres to the following envelope:

```json
{
  "event_id": "evt_98127391",
  "timestamp": "2026-11-16T07:30:00.123Z",
  "type": "AGENT_STEP | TOOL_CALL | TELEMETRY | APPROVAL_REQUEST | NOTIFICATION",
  "agent_id": "scout-01",
  "payload": {}
}
```

---

## 3. Tauri Native IPC Commands

The Tauri frontend communicates directly with the Rust native layer via `invoke()`:

| Command                     | Arguments                           | Return Type                            | Description                                                                                                 |
| :-------------------------- | :---------------------------------- | :------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `get_app_info`              | None                                | `AppInfo`                              | Returns validated application name, version, Tauri version, OS, and CPU architecture.                       |
| `get_desktop_status`        | None                                | `DesktopStatus`                        | Returns application metadata, active task counter, and current desktop settings.                            |
| `open_artifact_location`    | `relative_or_absolute: string`      | `Result<bool, string>`                 | Opens an application folder in Windows Explorer with directory traversal protection.                        |
| `test_notification`         | `title?: string, body?: string`     | `Result<bool, string>`                 | Dispatches native Windows 11 Action Center toast notification via `tauri-plugin-notification`.              |
| `get_backend_status`        | None                                | `BackendProcessStatus`                 | Queries supervisor state machine (`Ready`, `Restarting`, etc.), PID, port, uptime, and crash restart count. |
| `restart_backend`           | None                                | `Result<BackendProcessStatus, string>` | Triggers supervisor child process termination, backoff reset, and fresh spawn.                              |
| `get_window_preferences`    | None                                | `DesktopSettings`                      | Retrieves persistent preferences from `%LOCALAPPDATA%\AUTONOM\config\desktop_settings.json`.                |
| `set_window_preferences`    | `payload: UpdatePreferencesPayload` | `Result<DesktopSettings, string>`      | Updates preferences (close-to-tray, start-at-login, notifications, window bounds).                          |
| `save_current_window_state` | None                                | `Result<(), string>`                   | Queries active window position and size, clamping coordinates and persisting to disk.                       |

---

## 4. Command Center Dashboard Endpoints (Stage 08)

Authenticated HTTP endpoints under `/api/v1/dashboard/`:

| Method | Endpoint                          | Description                                                                                                                                              |
| :----- | :-------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET`  | `/api/v1/dashboard/overview`      | Returns system status, uptime, task summaries, agent operation statuses, recruitment pipeline histogram, worker pool capacity, and pending action items. |
| `GET`  | `/api/v1/dashboard/task-trends`   | Returns task creation, completion, and failure counts bucketed by time (`today`, `7d`, `30d`) with derived success rates.                                |
| `GET`  | `/api/v1/dashboard/activity`      | Returns recent durable task state transition events recorded in the SQLite audit ledger.                                                                 |
| `GET`  | `/api/v1/tasks/{task_id}/history` | Returns state transition history for a specific task.                                                                                                    |
| `POST` | `/api/v1/tasks/{task_id}/cancel`  | Cooperatively cancels a queued or executing background task.                                                                                             |

---

## 5. Module Workspace Endpoints (Stage 09)

Authenticated HTTP endpoints under `/api/v1/jobs`, `/api/v1/applications`, and `/api/v1/artifacts`:

| Method | Endpoint                          | Description                                                                                         |
| :----- | :-------------------------------- | :-------------------------------------------------------------------------------------------------- |
| `GET`  | `/api/v1/jobs`                    | Lists persistent job listings from SQLite with optional `status`, `company`, `limit`, and `offset`. |
| `GET`  | `/api/v1/jobs/{job_id}`           | Retrieves complete details of a specific job listing.                                               |
| `GET`  | `/api/v1/applications`            | Lists job applications with nested attempt histories, job metadata, and status filtering.           |
| `GET`  | `/api/v1/applications/{app_id}`   | Retrieves full details and execution attempt logs for a specific application.                       |
| `GET`  | `/api/v1/artifacts`               | Lists persisted artifacts with file size, SHA-256 checksums, and retention classes.                 |
| `GET`  | `/api/v1/artifacts/{artifact_id}` | Retrieves metadata for a specific persistent artifact.                                              |

---

## 5. Module Workspace Endpoints (Stage 09)

Authenticated HTTP endpoints under `/api/v1/jobs`, `/api/v1/applications`, and `/api/v1/artifacts`:

| Method | Endpoint                          | Description                                                                                         |
| :----- | :-------------------------------- | :-------------------------------------------------------------------------------------------------- |
| `GET`  | `/api/v1/jobs`                    | Lists persistent job listings from SQLite with optional `status`, `company`, `limit`, and `offset`. |
| `GET`  | `/api/v1/jobs/{job_id}`           | Retrieves complete details of a specific job listing.                                               |
| `GET`  | `/api/v1/applications`            | Lists job applications with nested attempt histories, job metadata, and status filtering.           |
| `GET`  | `/api/v1/applications/{app_id}`   | Retrieves full details and execution attempt logs for a specific application.                       |
| `GET`  | `/api/v1/artifacts`               | Lists persisted artifacts with file size, SHA-256 checksums, and retention classes.                 |
| `GET`  | `/api/v1/artifacts/{artifact_id}` | Retrieves metadata for a specific persistent artifact.                                              |
