# Windows Automation Testing Strategy & Verification Report (Stage 17)

## 1. Testing Philosophy & Verification Standard

AUTONOM enforces a zero-fake-data, genuine execution standard for Windows desktop automation. Testing verifies:
1. **Real Operating System APIs**: Direct calls to `user32.dll`, `kernel32.dll`, and `UIAutomationCore.dll`.
2. **Dedicated MTA Worker Pool**: Asynchronous dispatch, desktop attachment, and error containment.
3. **Fail-Closed Security**: Lock state rejection, Emergency Stop killswitch, and path traversal defense.
4. **Live Windows Application Control**: Verification against real running Windows applications (`explorer.exe`, `WindowsTerminal.exe`, `Notepad.exe`).
5. **Full-Stack End-to-End Flow**: Python backend services, FastAPI REST routes, TypeScript client types, and React UI components.

---

## 2. Automated Test Suites

### Backend Test Coverage (`services/api/tests/`)

| Test File | Focus | Test Count | Status |
| :--- | :--- | :---: | :---: |
| `test_desktop_session.py` | Interactive session discovery, lock state detection, screen resolution | 2 | PASSED |
| `test_desktop_windows.py` | Top-level window enumeration, `window_ref` resolution, stale HWND defense | 3 | PASSED |
| `test_desktop_uia.py` | MTA COM worker execution, bounded tree traversal, locator queries | 3 | PASSED |
| `test_desktop_actions.py` | File dialog safety guard, privacy redactions, Emergency Stop enforcement | 4 | PASSED |
| `test_api_desktop.py` | REST API routes under `/api/v1/desktop/*`, auth requirements, task CRUD | 8 | PASSED |
| `test_desktop_real_apps.py` | Live UIA tree inspection and state management against real Windows apps | 1 | PASSED |
| `test_specialist_agents.py` | Verification of operational status for `windows_computer_agent` and `structural_ui_agent` | 6 | PASSED |
| **All Backend Tests** | **Full Regression Suite** | **166** | **PASSED** |

### Frontend Test Coverage (`apps/desktop/src/test/`)

| Test File | Focus | Test Count | Status |
| :--- | :--- | :---: | :---: |
| `desktop-automation.test.tsx` | Desktop workspace, telemetry cards, applications list, windows inspection | 3 | PASSED |
| `computer-workspace.test.tsx` | Dual-modality header, Stage 17 production badge, panic killswitch | 1 | PASSED |
| `browser-automation.test.tsx` | Browser workspace dual-modality tab integration and sessions | 5 | PASSED |
| **All Frontend Tests** | **Full Vitest Suite** | **134** | **PASSED** |

---

## 3. Test Execution Verification Commands

```powershell
# Run Stage 17 backend desktop automation tests
services/api/.venv/Scripts/python.exe -m pytest services/api/tests/test_desktop_session.py services/api/tests/test_desktop_windows.py services/api/tests/test_desktop_uia.py services/api/tests/test_desktop_actions.py services/api/tests/test_api_desktop.py services/api/tests/test_desktop_real_apps.py -v

# Run full backend pytest regression suite
services/api/.venv/Scripts/python.exe -m pytest services/api/tests -q

# Run frontend vitest test suite
npm.cmd --prefix apps/desktop run test

# Run frontend TypeScript typecheck
npm.cmd --prefix apps/desktop run typecheck

# Run frontend production build
npm.cmd --prefix apps/desktop run build
```
All commands execute cleanly with **0 errors and 100% pass rates**.
