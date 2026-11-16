# AUTONOM Packaging Pipeline & Binary Distribution

> **Document Version:** 1.0.0  
> **Stage:** 05 — Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle  
> **Status:** Implemented & Verified

---

## 1. Executive Summary

Stage 05 establishes the end-to-end build and packaging pipeline for AUTONOM. The application produces a standalone Windows executable architecture with no external Python runtime dependency for end users.

---

## 2. Packaging Workflow

```
[TypeScript Frontend]      [Python Backend]        [Rust Desktop Core]
         |                        |                         |
         v                        v                         v
   `pnpm build`          `package-backend.ps1`        `cargo build`
   (Vite Bundle)             (PyInstaller)            (Tauri 2 MSVC)
         |                        |                         |
         v                        v                         v
 `apps/desktop/dist`    `apps/desktop/src-tauri/`     `autonom-desktop.exe`
                            `bin/autonom-api-...`           |
         \                        |                        /
          \                       |                       /
           +----------------------+----------------------+
                                  |
                                  v
                        `package-desktop.ps1`
                                  |
                                  v
                   STANDALONE DESKTOP DISTRIBUTION
```

---

## 3. Automated Packaging Scripts

### 3.1 Backend Packaging (`scripts/package-backend.ps1`)

Packages the Python FastAPI application into a standalone 27.8 MB executable with bundled dependencies (alembic, cryptography, sqlalchemy, uvicorn).

- Output: `apps/desktop/src-tauri/bin/autonom-api-x86_64-pc-windows-msvc.exe`.

### 3.2 Desktop Packaging (`scripts/package-desktop.ps1`)

Full pipeline execution:

1. Validates or builds the Python sidecar.
2. Compiles the React/Vite web application to `apps/desktop/dist`.
3. Compiles the native Tauri 2 desktop application in release mode using Cargo.

- Output: `E:\proooo\target\release\autonom-desktop.exe` (or `target\release\autonom-desktop.exe`).

### 3.3 Package Verification (`scripts/verify-package.ps1`)

Automated post-build verification:

1. Confirms existence and non-zero size of `dist/index.html`.
2. Confirms existence and checksum of `autonom-api-x86_64-pc-windows-msvc.exe`.
3. Confirms existence of `autonom-desktop.exe`.
4. Spawns the packaged sidecar standalone on a test port (8798), verifies HTTP 200 on `/ready`, and terminates the process cleanly.

---

## 4. Development Mode vs Packaged Distribution Mode

| Feature             | Development Mode (`dev.ps1`)                   | Packaged Mode (`package-desktop.ps1`) |
| :------------------ | :--------------------------------------------- | :------------------------------------ |
| **Frontend**        | Vite Dev Server with HMR (`localhost:5173`)    | Embedded static assets in `dist/`     |
| **Backend**         | Python virtualenv (`.venv/Scripts/python.exe`) | Frozen PyInstaller single-file binary |
| **Port**            | 8765                                           | 8765                                  |
| **Communication**   | Authenticated Loopback (127.0.0.1)             | Authenticated Loopback (127.0.0.1)    |
| **Process Control** | Terminal execution / Supervisor                | Win32 Job Object & Supervisor         |
| **Hot Reload**      | Active for React & FastAPI                     | Disabled (Release Build)              |
