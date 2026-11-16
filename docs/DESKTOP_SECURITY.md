# AUTONOM Desktop Security, Process Boundaries, and Local Isolation

> **Document Version:** 1.0.0  
> **Stage:** 05 — Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle  
> **Status:** Implemented & Verified

---

## 1. Executive Summary

AUTONOM executes with local user privileges and exercises computer automation capabilities. Stage 05 implements rigorous security controls to enforce isolation between desktop components, restrict external network access, and protect user data.

---

## 2. Loopback Isolation Boundary

1. **Strict 127.0.0.1 Binding**: The Python backend sidecar binds exclusively to IPv4 loopback `127.0.0.1`.
   - Never binds to `0.0.0.0`, `::`, or public network adapters.
   - External machines on the local network cannot access or query the AUTONOM API.
2. **Ephemeral Bearer Authentication**:
   - Each session generates an authentication key passed to the sidecar at startup via the `--api-key` parameter.
   - All sensitive endpoints (`/api/v1/*`) reject unauthenticated requests with `401 Unauthorized`.
   - The desktop frontend injects the authorization token via the `Authorization: Bearer <key>` header on all requests.

---

## 3. Kernel-Enforced Process Containment

1. **Win32 Job Object Kill-On-Close**:
   - The desktop harness assigns the child sidecar process to a Win32 Job Object configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
   - This ensures that abnormal terminations, user logouts, or crash events trigger immediate kernel termination of all child processes.
2. **No Orphaned Subprocesses**:
   - Eliminates dangling Python, browser, or worker processes.
   - Prevents port hogging or state corruption on subsequent launches.

---

## 4. Native Command Validation & Traversal Protection

Tauri exposes native Rust commands to the frontend webview. Stage 05 enforces strict validation:

1. **`open_artifact_location` Validation**:
   - Rejects directory traversal payloads (e.g., `../../Windows/System32`).
   - Resolves target paths to canonical absolute paths.
   - Asserts that canonical target paths reside within `%LOCALAPPDATA%\AUTONOM`. Any attempt to access locations outside the AUTONOM sandbox fails with an error.
2. **Settings Sanitization**:
   - Window geometry settings are clamped to safe minimum bounds (width $\ge 1050$, height $\ge 650$).
   - Prevents invalid or zero-pixel window configurations.
