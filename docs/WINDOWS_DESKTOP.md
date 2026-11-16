# AUTONOM Windows Desktop Shell & Native Integration

> **Document Version:** 1.0.0  
> **Stage:** 05 — Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle  
> **Status:** Implemented & Verified

---

## 1. Executive Summary

AUTONOM is architected as an autonomous multi-agent Windows 11 desktop assistant. Stage 05 establishes a self-contained, enterprise-grade desktop harness powered by **Tauri 2 (Rust)**, hosting a **React/TypeScript** frontend and supervising a **Python/FastAPI** backend sidecar process.

The desktop runtime enforces:

1. **Single-Instance Execution**: Prevents multiple overlapping instances and port collisions by detecting secondary launches, focusing the primary window, and passing arguments.
2. **Win32 Job Object Containment**: Guarantees that all child processes (Python sidecar, worker threads, headless browsers) terminate cleanly when AUTONOM exits or crashes.
3. **Multi-Monitor DPI & Coordinate Safety**: Restores saved window geometry safely across multi-monitor layouts and prevents off-screen rendering.
4. **System Tray & Toast Integration**: Provides background execution via close-to-tray and native Windows 11 Action Center notifications.

---

## 2. Desktop Shell Architecture

```
+---------------------------------------------------------------------------------------+
|                                    WINDOWS 11 OS                                      |
+---------------------------------------------------------------------------------------+
|  [System Tray]  [Windows Action Center]  [Win32 Job Object]  [Single Instance Mutex]  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                            TAURI 2 DESKTOP HARNESS (RUST)                             |
|                                                                                       |
|  - main.rs / lib.rs: Application builder, plugin registration, window setup           |
|  - processes/supervisor.rs: State machine, health polling, crash recovery             |
|  - processes/job_object.rs: Win32 JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE                  |
|  - tray/menu.rs: Tray context menu & left-click window toggling                       |
|  - notifications/mod.rs: Windows toast dispatch with quiet hours support              |
|  - state/mod.rs: JSON settings persistence (%LOCALAPPDATA%\AUTONOM\config)            |
+---------------------------------------------------------------------------------------+
           |                                                      |
 (Tauri IPC / Events)                                   (Supervised Process)
           |                                                      |
           v                                                      v
+-----------------------------+              +------------------------------------------+
|  REACT 18 FRONTEND (DIST)   |              |        PYTHON BACKEND SIDECAR            |
|                             |              |                                          |
| - Command Center & Sidebar  |              | - Standalone PyInstaller Binary          |
| - Desktop Diagnostics UI    | <--- HTTP -- | - 127.0.0.1:8765 (Loopback Only)         |
| - Storage & Task Monitoring |  (Auth Token)| - FastAPI / Uvicorn ASGI Server          |
| - Settings & Preferences    |              | - SQLite WAL & DPAPI Encrypted Vault     |
+-----------------------------+              +------------------------------------------+
```

---

## 3. Window Lifecycle & Management

### 3.1 Initial Geometry & Constraint Enforcement

- **Default Resolution**: 1440x900 pixels.
- **Minimum Constraints**: 1050x650 pixels enforced by native window manager (`tauri.conf.json`).
- **Persistence Target**: `%LOCALAPPDATA%\AUTONOM\config\desktop_settings.json`.

```json
{
  "close_to_tray": true,
  "start_at_login": false,
  "notifications_enabled": true,
  "notify_on_task_completion": true,
  "notify_on_backend_events": true,
  "window": {
    "x": 100,
    "y": 100,
    "width": 1440,
    "height": 900,
    "maximized": false,
    "selected_module": "command-center"
  }
}
```

### 3.2 Multi-Monitor & DPI Coordinate Validation

Before restoring window position from persistent configuration:

- Rust queries available monitors through `window.available_monitors()`.
- Coordinates $(X, Y)$ are validated against monitor bounds.
- If the target monitor has been disconnected or the coordinates fall outside visible screen real estate, the window automatically falls back to centered positioning on the primary monitor.

### 3.3 Close-to-Tray Minimization

When `close_to_tray` is enabled in `desktop_settings.json`:

- Intercepting `WindowEvent::CloseRequested` cancels window destruction and invokes `window.hide()`.
- The application remains resident in the system notification area.
- Selecting **Exit AUTONOM** from the system tray menu performs a full shutdown, signaling the backend supervisor and terminating the Job Object.

---

## 4. Single-Instance Enforcement

Tauri's `tauri-plugin-single-instance` is registered during application initialization:

- When a user attempts to launch a second instance of `AUTONOM.exe`:
  1. The second process detects the existing instance via Windows named mutex.
  2. The primary process receives a single-instance callback with the launch arguments.
  3. The primary window is restored if minimized, unhidden if hidden in the tray, brought to the foreground, and focused.
  4. The secondary process exits immediately without spawning additional background sidecars or binding conflicting ports.

---

## 5. Security & Isolation

1. **Loopback Isolation**: The Python backend strictly binds to `127.0.0.1`. It never listens on `0.0.0.0` or external network adapters.
2. **Process Containment**: Win32 Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` guarantees no orphaned processes can survive desktop host termination.
3. **Directory Access Restrictions**: The `open_artifact_location` native command strictly checks paths against `%LOCALAPPDATA%\AUTONOM` to prevent directory traversal outside authorized application folders.
