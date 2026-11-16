# AUTONOM — Development Environment Setup & Engineering Guide

This document provides complete instructions for setting up, running, testing, and building AUTONOM on **Windows 11 (x64)**.

---

## 1. Prerequisites & System Requirements

AUTONOM is architected to run on a mid-range engineering workstation without requiring Docker, PostgreSQL, or Redis.

### Hardware Baseline

- **CPU**: x86_64 modern processor (Intel Core i7 / AMD Ryzen 7).
- **RAM**: 16 GB DDR5 system memory.
- **GPU**: NVIDIA GeForce RTX 4050 Laptop GPU (6 GB VRAM) or equivalent.
- **Storage**: Minimum 5 GB free SSD space.

### Software Prerequisites

1. **Operating System**: Windows 11 (64-bit).
2. **Microsoft Edge WebView2**: Pre-installed on Windows 11.
3. **Node.js**: v20+ or v22+ LTS (Verified: v24.13.1).
4. **pnpm**: v9+ (Verified: v12.9.1).
5. **Python**: v3.12+ (CPython 3.12.13 managed via `uv`).
6. **uv**: Fast Python package and virtual environment manager (`uv 0.11.18+`).
7. **Rust Toolchain**: Rust 1.80+ with Cargo (`cargo 1.100.0` with `stable-x86_64-pc-windows-gnu` or `stable-x86_64-pc-windows-msvc`).
8. **C/C++ Linker**: Visual Studio C++ Build Tools (`link.exe`) or MinGW-w64 (`gcc.exe`).

---

## 2. Quick Setup

Run the automated PowerShell setup script from an elevated or user PowerShell prompt:

```powershell
.\scripts\setup.ps1
```

### Manual Step-by-Step Installation

#### 1. Install Monorepo Node Dependencies

```powershell
pnpm install
```

#### 2. Initialize Python Backend Virtual Environment

```powershell
cd services/api
uv venv
uv pip install -e ".[dev]"
cd ../..
```

#### 3. Verify Rust Toolchain

```powershell
cd apps/desktop/src-tauri
cargo check
cd ../../..
```

---

## 3. Development Commands

### Running Services Concurrently

Use the development orchestration script to start both the Python backend and Tauri desktop shell with graceful shutdown:

```powershell
.\scripts\dev.ps1
```

### Running Services Independently

#### Terminal 1: Python FastAPI Backend Service

```powershell
pnpm dev:backend
# Or directly via Python:
cd services/api
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765 --reload
```

- Interactive Swagger API Documentation: `http://127.0.0.1:8765/docs`
- Service Health Endpoint: `http://127.0.0.1:8765/api/v1/health`
- Service Readiness Endpoint: `http://127.0.0.1:8765/api/v1/ready`
- Service Version Endpoint: `http://127.0.0.1:8765/api/v1/version`

#### Terminal 2: React Frontend (Vite Browser Mode)

```powershell
pnpm dev
# Opens at: http://127.0.0.1:5173
```

#### Terminal 3: Tauri Desktop Application

```powershell
pnpm dev:desktop
# Compiles Rust harness and launches native Windows window
```

---

## 4. Testing & Quality Verification

### Run All Tests

```powershell
.\scripts\test.ps1
```

### Run Tests by Component

- **Frontend Vitest**: `pnpm test:frontend`
- **Backend Pytest**: `pnpm test:backend`
- **Native Rust**: `cd apps/desktop/src-tauri && cargo test`

### Run All Quality & Lint Checks

```powershell
.\scripts\check.ps1
```

Executes:

1. Stage 01 Architectural Validation (`scripts/validate_stage01.py`)
2. TypeScript Strict Compilation (`pnpm typecheck`)
3. Prettier Formatting (`pnpm format:check`)
4. Ruff Python Linter (`ruff check .`)
5. Pytest Unit Tests
6. Cargo Fmt Check (`cargo fmt --all -- --check`)
7. Cargo Clippy Lint (`cargo clippy`)

---

## 5. Production Build

To compile production assets:

```powershell
.\scripts\build.ps1
```

- **Frontend Assets**: Output to `apps/desktop/dist/`.
- **Native Binary**: Output to `apps/desktop/src-tauri/target/release/autonom-desktop.exe`.

> [!NOTE]
> Full Windows installer creation (MSIX / NSIS) with code signing is scheduled for **Stage 50**.

---

## 6. Troubleshooting & Common Issues

### Issue: Port 8765 or 5173 Already in Use

- **Symptom**: `dev.ps1` reports port conflict.
- **Resolution**:
  ```powershell
  Get-NetTCPConnection -LocalPort 8765 -State Listen | Select-Object OwningProcess
  Stop-Process -Id <PID> -Force
  ```

### Issue: Rust Linker `link.exe not found`

- **Symptom**: Cargo compilation fails looking for MSVC linker.
- **Resolution**:
  Switch Rust to the GNU toolchain which pairs with MinGW-W64 GCC:
  ```powershell
  rustup toolchain install stable-x86_64-pc-windows-gnu
  rustup default stable-x86_64-pc-windows-gnu
  ```

### Issue: Backend Status Displays "DISCONNECTED" in UI

- **Symptom**: Red badge in top header.
- **Resolution**:
  1. Ensure the backend is running (`curl http://127.0.0.1:8765/api/v1/health`).
  2. Verify CORS allows origin `http://127.0.0.1:5173` or `tauri://localhost`.
  3. Click "Check Status" in the Command Center to trigger immediate retry.

---

## 7. Current Stage Limitations (Stage 02)

- Multi-agent swarm planning, computer vision capture, and automated job scraping belong to later stages.
- The UI in Stage 02 is an information-dense, real development status center displaying genuine local environment diagnostics.
