# AUTONOM — Automation Controls, Task Dispatch & Worker Pool Management

## 1. Overview & Architectural Role

The Automation Controls architecture established in **Stage 10** governs background task dispatch, worker concurrency bounds, queue limits, circuit breakers, and power awareness for the AUTONOM system.

These controls ensure that autonomous operations (e.g. background web scraping, document generation, application processing) execute reliably without overwhelming workstation hardware, exhausting network bandwidth, or causing desktop stutter.

```
+-----------------------------------------------------------------------------------------+
|                              FRONTEND: /settings/automation                             |
| - Worker Concurrency Slider (1 to 8 workers, default 3)                                 |
| - Task Queue Capacity (10 to 500 tasks, default 100)                                    |
| - Circuit Breaker Thresholds (Error rate %, Failure count, Cooldown duration)           |
| - Power Management (Pause on Battery Power, Throttle on High CPU/RAM)                   |
| - Global Automation Pause / Resume Switch                                               |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v PATCH /api/v1/settings/automation
+-----------------------------------------------------------------------------------------+
|                               FASTAPI LOCAL BACKEND (8765)                              |
| - AutomationSettings Pydantic Schema Validation                                         |
| - Dynamic Worker Pool Throttle & Queue Limit Adjustment                                 |
| - Circuit Breaker State Machine Evaluation                                              |
| - Power Status Monitoring (Windows Power Management APIs)                               |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Configuration Schema Specification (`AutomationSettings`)

The configuration model is declared in `services/api/app/schemas/settings.py` and mirrored in `packages/shared-types/src/settings.ts`:

```typescript
export interface AutomationSettings {
  // Global Engine State
  automation_enabled: boolean; // Master enable/pause toggle

  // Worker Pool Sizing
  max_concurrent_workers: number; // 1 - 8 (Default: 3)
  task_queue_capacity: number; // 10 - 500 (Default: 100)
  worker_poll_interval_ms: number; // 250 - 5000 (Default: 1000)

  // Execution & Timeout Guards
  task_default_timeout_seconds: number; // 30 - 3600 (Default: 600)
  max_retries_per_task: number; // 0 - 5 (Default: 3)
  retry_backoff_factor: number; // 1.0 - 5.0 (Default: 2.0 exponential)

  // Circuit Breaker Guardrails
  circuit_breaker_enabled: boolean; // Default: true
  consecutive_failure_threshold: number; // 2 - 20 (Default: 5)
  failure_rate_threshold_percent: number; // 10 - 90 (Default: 40)
  cooldown_period_seconds: number; // 30 - 1800 (Default: 300)

  // Hardware & Power Awareness
  pause_on_battery: boolean; // Default: true (conserve laptop battery)
  battery_level_threshold_percent: number; // 10 - 50 (Default: 20)
  throttle_on_high_system_load: boolean; // Default: true
  cpu_threshold_percent: number; // 50 - 95 (Default: 85)
  ram_threshold_percent: number; // 50 - 95 (Default: 85)
}
```

---

## 3. Worker Pool Concurrency & Resource Boundaries

### 3.1 Hardware Concurrency Bounds (1–8 Workers)

To protect host workstation stability:

- **Minimum**: 1 worker (strictly sequential execution).
- **Default**: 3 workers (optimal balance for 6-core/12-thread or 8-core laptops with 16GB RAM).
- **Maximum**: 8 workers (strictly capped to prevent thread starvation and excessive memory pressure from concurrent browser instances).

### 3.2 Dynamic Throttling Under High System Load

When `throttle_on_high_system_load: true`:

1. The backend background monitor inspects live CPU and RAM consumption every 5 seconds.
2. If CPU utilization exceeds `cpu_threshold_percent` (85%) or RAM exceeds `ram_threshold_percent` (85%), active worker concurrency is dynamically reduced to 1.
3. If pressure persists for >60 seconds, task dispatch is temporarily held until host load normalizes.

### 3.3 Laptop Battery Power Awareness

When running on mobile hardware:

- If `pause_on_battery: true` and the Windows AC power line is disconnected, intensive browser automation and model inference tasks are automatically paused.
- If battery level falls below `battery_level_threshold_percent` (default 20%), all background workers are drained to prevent sudden workstation shutdown during critical operations.

---

## 4. Circuit Breaker Architecture

To prevent runaway retry storms (e.g. repeated failed application submissions due to network dropouts or website anti-bot challenges):

```
+----------------+  Failure Count >= 5   +----------------+
|     CLOSED     | --------------------> |      OPEN      |
| Normal Dispatch|                       | Dispatch Halted|
+----------------+                       +----------------+
        ^                                        |
        | Success (Probe Passes)                 | Cooldown (300s)
        |                                        v
+----------------+                       +----------------+
|   HALF-OPEN    | <-------------------- |   COOLDOWN     |
| Test 1 Task    |                       | Elapsed        |
+----------------+
```

1. **Closed (Normal)**: Tasks execute as scheduled.
2. **Open (Tripped)**: When consecutive failures reach `consecutive_failure_threshold` (default 5) or error rate exceeds `failure_rate_threshold_percent` (default 40% over 10 tasks), the circuit trips to `OPEN`.
   - Dispatch halts immediately.
   - A critical alert banner appears on the Command Center and Settings pages.
   - The user is notified via Windows Action Center toast.
3. **Cooldown & Half-Open**:
   - The circuit remains open for `cooldown_period_seconds` (default 300s).
   - Once elapsed, the state moves to `HALF-OPEN`, allowing a single probe task to execute.
   - If successful, the circuit resets to `CLOSED`; if failed, it returns to `OPEN` for another cooldown cycle.

---

## 5. Global Pause & Hotkey Integration

AUTONOM provides multiple independent mechanisms to halt autonomous activity:

1. **Software Toggle**: Accessible at the top of [AutomationSettingsPage.tsx](file:///e:/proooo/AUTO%20JOB/apps/desktop/src/features/settings/pages/AutomationSettingsPage.tsx) and the Command Center header.
2. **Global Physical Hotkey (`Pause / Break`)**: Registered via the Tauri native shortcut manager, immediately triggering `/api/v1/automation/pause`.
3. **Emergency Abort (`Ctrl+Alt+Esc`)**: Hard terminates active child browser processes and drains the worker pool within 500ms.

---

## 6. Restart vs. Live Hot-Reload Policy

The table below documents which settings apply immediately versus those requiring backend or supervisor restarts:

| Setting Field             | Hot-Reloadable?           | Behavior on Update                                            |
| ------------------------- | ------------------------- | ------------------------------------------------------------- |
| `automation_enabled`      | **Yes**                   | Instant pause/resume of the task dispatcher loop              |
| `max_concurrent_workers`  | **Yes**                   | Worker pool adjusts capacity without terminating active tasks |
| `circuit_breaker_enabled` | **Yes**                   | Circuit breaker state machine reconfigures immediately        |
| `pause_on_battery`        | **Yes**                   | Power state listener toggles immediately                      |
| `worker_poll_interval_ms` | **No (Restart Required)** | Timer loop interval compiled on backend service startup       |
| `task_queue_capacity`     | **No (Restart Required)** | SQLite in-memory ring buffer sized during repository init     |
