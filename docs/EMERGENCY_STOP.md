# AUTONOM Global Emergency Stop & Automation Pause

## 1. Architectural Distinction: Emergency Stop vs. Automation Pause

AUTONOM separates hard aborts from cooperative workflow pauses:

| Feature | Emergency Stop | Automation Pause |
|---|---|---|
| **Impact** | Halts all active operations, aborts steps, blocks all execution | Prevents new dispatches; allows active running steps to finish |
| **Fail-Closed** | Yes; fail-closed invariant enforced in-memory and in SQLite | No; graceful queue draining |
| **Memory / State** | Discards in-flight ephemeral state; freezes approvals | Preserves all workflow DAG states and context |
| **Persistence** | Persists across process crashes and restarts in SQLite | In-memory with SQLite fallback |
| **API Trigger** | `POST /api/v1/security/emergency-stop` | `POST /api/v1/security/automation/pause` |
| **UI Control** | Red Emergency Stop button & pulsing header banner | Pause/Resume Dispatch button |
| **Tray Control** | Tray menu "EMERGENCY STOP (Halt Swarm)" | Tray menu "Pause / Resume Automation" |

---

## 2. Hard Emergency Stop Implementation

The `EmergencyStopController` (`app.security.authorization.emergency.EmergencyStopController`) maintains a thread-safe singleton state synchronized with SQLite (`emergency_stop_state`):

```python
class EmergencyStopController:
    @property
    def is_emergency_stop_active(self) -> bool:
        return self._is_emergency_stop_active

    async def activate_emergency_stop(self, activated_by: str = "operator", reason: str | None = None) -> EmergencyStopState:
        self._is_emergency_stop_active = True
        # Persist to SQLite
        async with get_db_session() as session:
            repo = AuthorizationRepository(session)
            await repo.set_emergency_stop_state(is_active=True, ...)
        # Abort background scheduler loops
        return self.get_state()
```

### Restart Survivability
When the FastAPI backend boots up, `ServiceContainer` initializes the `EmergencyStopController`. It queries SQLite for any pre-existing active emergency stop flag. If found, the application starts in an already-stopped state, preventing rogue agent dispatches upon service recovery.
