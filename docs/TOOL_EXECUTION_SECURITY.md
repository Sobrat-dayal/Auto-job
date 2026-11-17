# AUTONOM Secure Tool Execution Gateway

## 1. Gateway Wrapper Architecture

The `ToolExecutionGateway` (`app.security.enforcement.gateway.ToolExecutionGateway`) is the authoritative choke point between the multi-agent orchestration runtime (`ExecutionScheduler`) and native system tools, LLM calls, filesystem writes, and network sockets:

```
  ExecutionScheduler ──► ToolExecutionGateway.execute_capability()
                                   │
                                   ├── 1. Construct ActorContext (Runtime-Derived)
                                   ├── 2. Evaluate Request in AuthorizationEngine
                                   │      ├── Outcome ALLOW? Continue.
                                   │      ├── Outcome REQUIRE_APPROVAL? Submit & raise AuthorizationRequiredError.
                                   │      └── Outcome DENY? Raise PermissionError.
                                   │
                                   ├── 3. Pre-Execution Just-In-Time TOCTOU Check:
                                   │      Verify Emergency Stop is NOT engaged right before calling tool.
                                   │
                                   ├── 4. Execute Custom Handler or Capability Handler
                                   │
                                   ├── 5. Post-Execution Approval Consumption:
                                   │      Transition approval record from 'approved' to 'consumed'.
                                   │
                                   └── 6. Audit Decision Record Written to SQLite
```

---

## 2. Time-of-Check to Time-of-Use (TOCTOU) Defense

Between the moment authorization is evaluated and the moment a long-running tool starts executing, system state may change (e.g. operator hits Emergency Stop).

The `ToolExecutionGateway` defends against this window by performing a secondary just-in-time check:
```python
if self.emergency_controller.is_emergency_stop_active:
    raise RuntimeError("Emergency Stop engaged prior to capability dispatch")
```
If Emergency Stop was engaged while the request was in flight, the operation is immediately aborted without executing the underlying handler.

---

## 3. Actor Context Provenance

Agent identity is strictly derived from the execution environment:
- Agent ID and Workflow ID are populated from the active DAG execution state.
- Client applications cannot spoof `actor_type="user"` or change `agent_id` inside parameter payloads.
- All decisions record this tamper-evident context in SQLite.
