# Procedure Security & Authorization Governance

## 1. Overview & Core Tenet

Autonomous procedure recording and execution interact with native operating system handles, credentials, user inputs, and external web APIs. Security cannot be an afterthought.

The Workflow Reliability Engine integrates directly with AUTONOM's Stage 14 Authorization Engine, enforcing:
1. **Role-Based Permission Checks**: Fine-grained capability checks on recording and execution.
2. **Global Emergency Stop Integration**: Immediate interruption upon triggering the desktop or hardware killswitch.
3. **Session Lock Guardrails**: Automatic suspension if the Windows user workstation locks.
4. **Secret Parameter Isolation**: Mandatory encryption and DPAPI vault protection for secret variables.

---

## 2. Capability Permissions & Default Policies

Stage 20 introduces 5 core capabilities registered with the Stage 14 `CapabilityRegistry`:

| Capability ID | Risk Level | Description | Default Policy |
| :--- | :--- | :--- | :--- |
| `reliability_start_recording` | `LOW` | Initiates scoped interaction recording. | Preauthorized for standard operators. |
| `reliability_stop_recording` | `LOW` | Terminates active recording session. | Preauthorized for standard operators. |
| `reliability_compile_procedure` | `LOW` | Compiles recorded session into a procedure draft. | Preauthorized for standard operators. |
| `reliability_execute_procedure` | `MODERATE` | Replays a procedure against live software. | Requires policy check or user confirmation if risk > 70. |
| `reliability_resume_execution` | `MODERATE` | Continues an interrupted execution from checkpoint. | Requires confirmation if uncertain side effects exist. |

---

## 3. Emergency Stop Integration

The Stage 14 Global Emergency Stop (`EmergencyStopManager`) acts as an immediate circuit breaker:

```python
class ProcedureExecutionGuard:
    def __init__(self, emergency_stop_mgr: EmergencyStopManager):
        self.emergency_stop_mgr = emergency_stop_mgr

    def assert_safe_to_execute(self, execution_id: str) -> None:
        if self.emergency_stop_mgr.is_active():
            raise EmergencyStopActiveError("Emergency stop is active; procedure execution aborted.")
```

During step execution, before every single step dispatch:
1. The executor invokes `assert_safe_to_execute()`.
2. If the user hits the desktop Emergency Stop button or the hardware `Pause/Break` key, the engine aborts the active step, writes a final `EmergencyStop` checkpoint to SQLite, and transitions the execution state to `ABORTED`.

---

## 4. Windows Workstation Session Lock Detection

Replaying automated keystrokes or mouse clicks into a locked Windows workstation creates severe security risks (such as typing credentials into the Windows login screen or failing to verify target applications).

Before dispatching physical input:
```python
def is_workstation_locked() -> bool:
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hdesk = user32.OpenInputDesktop(0, False, 0x0100)
        if hdesk == 0:
            return True  # Desktop locked or switch desktop active
        user32.CloseDesktop(hdesk)
        return False
    except Exception:
        return False
```

If `is_workstation_locked()` returns `True`, execution immediately pauses and generates an alert event.

---

## 5. Audit Logging & Immutable Lineage

All procedure executions, checkpoint creations, and recovery actions are logged to the SQLite `security_audit_events` ledger with:
- `actor_id` (agent or user initiating run)
- `procedure_id` and `version`
- `execution_id`
- `target_applications`
- `side_effects_recorded`
- `policy_decision` (`GRANTED` / `DENIED`)
