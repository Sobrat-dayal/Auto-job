# AUTONOM Backend Sidecar Architecture & Packaging

> **Document Version:** 1.0.0  
> **Stage:** 05 — Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle  
> **Status:** Implemented & Verified

---

## 1. Overview

AUTONOM combines a high-performance Rust/Tauri desktop shell with a Python/FastAPI backend sidecar. Rather than requiring users to install Python, pip, or virtual environments manually, the backend is packaged into a self-contained Windows executable via **PyInstaller**.

The desktop host transparently supervises the sidecar:

- Spawns it upon desktop startup.
- Injects loopback parameters (`--host 127.0.0.1`, `--port 8765`, `--api-key <ephemeral-token>`).
- Encloses it within a Win32 Job Object.
- Polls readiness before loading the user interface.
- Automatically recovers and restarts the sidecar in case of unhandled crashes.

---

## 2. Standalone Entry Point (`services/api/app/server_entry.py`)

The backend sidecar CLI entry point provides explicit command-line flags for desktop host integration:

```python
parser.add_argument("--host", default="127.0.0.1", help="Loopback host to bind")
parser.add_argument("--port", type=int, default=8765, help="Port to bind")
parser.add_argument("--api-key", default=None, help="Local API authentication key")
parser.add_argument("--log-level", default="info", help="Logging level")
```

When started with `--api-key`, the sidecar enforces local Bearer token authorization across all sensitive endpoints (`/api/v1/*`), while exposing `/health`, `/ready`, and `/version` for supervisor polling without authentication.

---

## 3. Sidecar Discovery Hierarchy (`apps/desktop/src-tauri/src/processes/sidecar.rs`)

The Tauri desktop harness uses a multi-tier resolution strategy to locate the sidecar binary:

```
+-------------------------------------------------------------------------+
|                  1. PACKAGED SIDECAR BINARY CHECK                       |
|   Check if running from release bundle:                                 |
|   <app_dir>/bin/autonom-api-x86_64-pc-windows-msvc.exe                 |
+-------------------------------------------------------------------------+
                                    |
                            (If Not Present)
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  2. LOCAL WORKSPACE BINARY CHECK                        |
|   Check workspace sidecar bin directory:                                |
|   apps/desktop/src-tauri/bin/autonom-api-x86_64-pc-windows-msvc.exe    |
+-------------------------------------------------------------------------+
                                    |
                            (If Not Present)
                                    |
                                    v
+-------------------------------------------------------------------------+
|               3. DEVELOPMENT VIRTUALENV FALLBACK                        |
|   Execute via Python venv:                                              |
|   services/api/.venv/Scripts/python.exe -m uvicorn app.main:app         |
+-------------------------------------------------------------------------+
```

This guarantees seamless operation both during rapid developer iteration (using hot reload in `.venv`) and in production packaged installations (using the frozen executable).

---

## 4. PyInstaller Packaging Pipeline (`scripts/package-backend.ps1`)

The packaging script executes:

```powershell
& pyinstaller `
    --name autonom-api `
    --onefile `
    --clean `
    --noconfirm `
    --icon="$DesktopDir\icons\icon.ico" `
    --hidden-import "uvicorn.logging" `
    --hidden-import "uvicorn.loops" `
    --hidden-import "uvicorn.loops.auto" `
    --hidden-import "uvicorn.protocols" `
    --hidden-import "uvicorn.protocols.http" `
    --hidden-import "uvicorn.protocols.http.auto" `
    --hidden-import "uvicorn.protocols.websockets" `
    --hidden-import "uvicorn.protocols.websockets.auto" `
    --hidden-import "uvicorn.lifespan" `
    --hidden-import "uvicorn.lifespan.on" `
    --hidden-import "alembic" `
    --hidden-import "app.main" `
    --collect-all "app" `
    --collect-all "cryptography" `
    "$ApiDir\app\server_entry.py"
```

The resulting 27.8 MB binary is copied to:

- `apps/desktop/src-tauri/bin/autonom-api-x86_64-pc-windows-msvc.exe`
- `apps/desktop/src-tauri/bin/autonom-api-x86_64-pc-windows-gnu.exe`

---

## 5. Verification & Testing

The packaged sidecar can be tested independently via:

```powershell
.\apps\desktop\src-tauri\bin\autonom-api-x86_64-pc-windows-msvc.exe --help
```

Or launched against test ports for automated health verification via `scripts/verify-package.ps1`.
