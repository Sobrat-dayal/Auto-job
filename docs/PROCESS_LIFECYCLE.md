# AUTONOM Process Supervision, Crash Recovery, and Lifecycle Management

> **Document Version:** 1.0.0  
> **Stage:** 05 — Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle  
> **Status:** Implemented & Verified

---

## 1. Executive Summary

Autonomous computer control and multi-agent systems require rigorous process isolation and lifecycle control. A crashed backend must not crash the desktop host, and a terminated desktop host must never leave orphaned Python or browser processes consuming CPU and GPU resources.

Stage 05 implements:

1. **Kernel-Level Win32 Job Object Limits**: Guarantees zero orphaned processes on any shutdown or abnormal crash.
2. **State Machine Supervisor**: Coordinates backend states (`Stopped`, `Starting`, `Connecting`, `Ready`, `Degraded`, `Restarting`, `Failed`, `Stopping`).
3. **Bounded Exponential Backoff Recovery**: Restarts unexpectedly killed sidecars up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s).
4. **Task State Reconciliation**: Leverages Stage 04 SQLite persistence to restore queued, in-progress, and completed tasks seamlessly upon recovery.

---

## 2. Win32 Job Object Containment (`processes/job_object.rs`)

Windows Job Objects provide operating system-enforced process grouping. AUTONOM creates an anonymous Job Object at startup and applies `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`:

```rust
let mut info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;

SetInformationJobObject(
    self.handle,
    JobObjectExtendedLimitInformation,
    &info as *const _ as *const _,
    std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
);
```

When the sidecar is spawned, its process handle is assigned to the Job Object via `AssignProcessToJobObject`.

- If `AUTONOM.exe` terminates normally: the Job Object handle closes, and Windows terminates the sidecar.
- If `AUTONOM.exe` crashes or is killed via Task Manager: the Windows kernel automatically terminates all processes in the Job Object. No orphaned `python.exe` or `autonom-api.exe` processes can remain.

---

## 3. Supervisor State Machine

```
              +-------------+
              |   Stopped   |
              +-------------+
                     |
                 (start)
                     v
              +-------------+
              |  Starting   |<--------------------+
              +-------------+                     |
                     |                            |
               (child spawned)                    |
                     v                            |
              +-------------+                     |
              | Connecting  |                     | (Exponential
              +-------------+                     |  Backoff
                     |                            |  Recovery)
              (poll /ready ok)                    |
                     v                            |
              +-------------+                     |
    +-------->|    Ready    |                     |
    |         +-------------+                     |
    |                |                            |
(recover)     (unhandled exit)                    |
    |                v                            |
    |         +-------------+                     |
    |         | Restarting  |---------------------+
    |         +-------------+
    |                |
    |         (max restarts
    |          exceeded)
    |                v
    |         +-------------+
    +---------|   Failed    |
              +-------------+
```

### 3.1 State Definitions

- **Stopped**: No backend process is running.
- **Starting**: Sidecar executable located and command configured.
- **Connecting**: Child process running, polling `/ready` endpoint on loopback.
- **Ready**: Backend returned `ready: true`, database and workers confirmed healthy.
- **Degraded**: Backend reachable but some subsystem checks reporting false.
- **Restarting**: Unhandled child termination detected, performing exponential backoff delay before respawn.
- **Failed**: Max restarts (5) exceeded. User intervention required via UI.
- **Stopping**: Graceful shutdown in progress, SIGTERM sent.

---

## 4. Crash Recovery & Task State Reconciliation

When the background exit monitor thread detects that the sidecar process exited unexpectedly:

1. It records the exit code and updates state to `Restarting`.
2. It increments `restart_count`. If `restart_count > max_restarts (5)`, state transitions to `Failed` and an error notification is sent.
3. It computes backoff delay: $\Delta t = \min(1.0 \times 2^{\text{restart\_count}-1}, 16.0)\text{ seconds}$.
4. Upon expiration, a fresh child process is spawned and assigned to the Job Object.
5. Readiness polling waits for `/ready`.
6. Once online, the sidecar reopens the SQLite database with WAL mode:
   - Any tasks that were `running` when the crash occurred are evaluated during reconciliation.
   - Idempotent recovery transitions interrupted tasks to `interrupted` or resumes them according to task policy.
   - Completed tasks remain untouched and accessible to the frontend.

---

## 5. Graceful Application Termination

When the user initiates application exit (via System Tray or window close when close-to-tray is disabled):

1. Desktop host invokes `supervisor.stop()`.
2. Rust sends a termination signal to the child process.
3. Child process lifespan shutdown hooks execute, completing pending database writes and closing connection pools.
4. If child does not terminate within 4 seconds, `child.kill()` is called.
5. Job Object handle is dropped.
