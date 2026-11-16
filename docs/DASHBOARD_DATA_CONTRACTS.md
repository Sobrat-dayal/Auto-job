# AUTONOM — Dashboard API Data Contracts (Stage 08)

## 1. Overview

The Command Center communicates with the FastAPI backend over authenticated loopback HTTP (`http://127.0.0.1:8765/api/v1/dashboard/*`) and Server-Sent Events (`http://127.0.0.1:8765/api/v1/events/stream`).

All responses conform to strictly typed Pydantic models in Python (`services/api/app/schemas/dashboard.py`) and TypeScript interfaces in React (`apps/desktop/src/types/dashboard.ts`).

---

## 2. API Endpoints

### 2.1 `GET /api/v1/dashboard/overview`

Retrieves consolidated telemetry for the Command Center.

#### Request Headers

```http
Authorization: Bearer <AUTONOM_API_TOKEN>
Accept: application/json
```

#### Response Model (`DashboardOverviewResponse`)

```json
{
  "system_status": "operational",
  "uptime_seconds": 142.5,
  "backend_connected": true,
  "task_dispatch_status": "active",
  "ai_swarm_status": "scheduled_stage_12",
  "tasks_summary": {
    "running": 1,
    "queued": 0,
    "completed": 12,
    "failed": 1,
    "cancelled": 0,
    "total": 14
  },
  "agents": [
    {
      "id": "agent-discovery",
      "name": "Job Discovery Agent",
      "role": "Scouting & Feed Scraping",
      "status": "unavailable",
      "target_stage": "Stage 26",
      "is_available": false,
      "current_task": null,
      "progress": null,
      "last_activity": null,
      "successful_tasks": 0,
      "failed_tasks": 0,
      "message": "Autonomous job scraping scheduled for activation in Stage 26."
    },
    {
      "id": "agent-tailor",
      "name": "Application Tailor Agent",
      "role": "Resume & Cover Letter Customization",
      "status": "unavailable",
      "target_stage": "Stage 30",
      "is_available": false,
      "current_task": null,
      "progress": null,
      "last_activity": null,
      "successful_tasks": 0,
      "failed_tasks": 0,
      "message": "Resume & cover letter generator scheduled for Stage 30."
    },
    {
      "id": "agent-swarm-lead",
      "name": "Supervisor Swarm Lead",
      "role": "Workflow Orchestration & Task Planning",
      "status": "unavailable",
      "target_stage": "Stage 12",
      "is_available": false,
      "current_task": null,
      "progress": null,
      "last_activity": null,
      "successful_tasks": 0,
      "failed_tasks": 0,
      "message": "Multi-agent supervisor swarm orchestrator scheduled for Stage 12."
    }
  ],
  "recruitment": {
    "jobs_discovered": 0,
    "jobs_discovered_today": 0,
    "active_listings": 0,
    "applications_total": 0,
    "applications_submitted": 0,
    "pipeline_stages": {
      "discovered": 0,
      "evaluated": 0,
      "matched": 0,
      "queued": 0,
      "preparing": 0,
      "submitted": 0,
      "recruiter_response": 0,
      "interview": 0,
      "offer": 0,
      "rejected": 0
    },
    "automated_scouting_enabled": false,
    "automated_scouting_message": "Automated scraping engine scheduled for activation in Stage 26."
  },
  "workers": {
    "total": 4,
    "active": 1,
    "idle": 3,
    "max_capacity": 4
  },
  "pending_actions_count": 1,
  "timestamp": "2026-11-16T22:30:00Z"
}
```

---

### 2.2 `GET /api/v1/dashboard/task-trends`

Retrieves time-bucketed task execution metrics aggregated from the SQLite `tasks` table.

#### Query Parameters

- `window` (optional, default: `"7d"`): Allowed values: `"today"`, `"7d"`, `"30d"`.

#### Response Model (`DashboardTaskTrendsResponse`)

```json
{
  "window": "7d",
  "data_points": [
    {
      "date": "2026-11-10",
      "completed": 4,
      "failed": 0,
      "created": 4
    },
    {
      "date": "2026-11-16",
      "completed": 8,
      "failed": 1,
      "created": 10
    }
  ],
  "total_volume": 14,
  "overall_success_rate": 88.9
}
```

---

### 2.3 `GET /api/v1/dashboard/activity`

Retrieves recent durable events recorded in the SQLite `task_events` audit ledger.

#### Query Parameters

- `limit` (optional, default: 50, max: 200).

#### Response Model

```json
[
  {
    "event_id": "ev-101",
    "event_type": "task.state_changed",
    "timestamp": "2026-11-16T22:25:01Z",
    "payload": {
      "task_id": "8a067a90-7d6f-4221-a02e-9d854ce695ec",
      "old_state": "queued",
      "new_state": "running"
    }
  }
]
```

---

### 2.4 `GET /api/v1/tasks/{task_id}/history`

Retrieves the complete state transition history for a specific task.

#### Response Model (`List[TaskHistoryEvent]`)

```json
[
  {
    "event_id": "d0444fc1-e737-4d11-8fc2-6c245642a8b3",
    "task_id": "8a067a90-7d6f-4221-a02e-9d854ce695ec",
    "event_type": "state_changed",
    "old_state": "queued",
    "new_state": "running",
    "timestamp": "2026-11-16T22:25:01Z",
    "details": null
  },
  {
    "event_id": "e1555fc2-f848-4e22-9fd3-7d356753b9c4",
    "task_id": "8a067a90-7d6f-4221-a02e-9d854ce695ec",
    "event_type": "completed",
    "old_state": "running",
    "new_state": "completed",
    "timestamp": "2026-11-16T22:25:05Z",
    "details": { "duration_seconds": 4.02 }
  }
]
```

---

## 3. TypeScript Interfaces (`apps/desktop/src/types/dashboard.ts`)

```typescript
export interface DashboardTasksSummary {
  running: number;
  queued: number;
  completed: number;
  failed: number;
  cancelled: number;
  total: number;
}

export type AgentOperationState =
  | 'unavailable'
  | 'offline'
  | 'idle'
  | 'starting'
  | 'planning'
  | 'running'
  | 'paused'
  | 'waiting_approval'
  | 'recovering'
  | 'completed'
  | 'failed'
  | 'degraded';

export interface AgentOperationStatus {
  id: string;
  name: string;
  role: string;
  status: AgentOperationState;
  target_stage: string;
  is_available: boolean;
  current_task?: string | null;
  progress?: number | null;
  last_activity?: string | null;
  successful_tasks: number;
  failed_tasks: number;
  message: string;
}

export interface RecruitmentSummary {
  jobs_discovered: number;
  jobs_discovered_today: number;
  active_listings: number;
  applications_total: number;
  applications_submitted: number;
  pipeline_stages: Record<string, number>;
  automated_scouting_enabled: boolean;
  automated_scouting_message: string;
}

export interface DashboardWorkersStatus {
  total: number;
  active: number;
  idle: number;
  max_capacity: number;
}

export interface DashboardOverviewResponse {
  system_status: 'operational' | 'degraded' | 'disconnected';
  uptime_seconds: number;
  backend_connected: boolean;
  task_dispatch_status: 'active' | 'paused';
  ai_swarm_status: 'scheduled_stage_12' | 'active' | 'degraded';
  tasks_summary: DashboardTasksSummary;
  agents: AgentOperationStatus[];
  recruitment: RecruitmentSummary;
  workers: DashboardWorkersStatus;
  pending_actions_count: number;
  timestamp: string;
}
```
