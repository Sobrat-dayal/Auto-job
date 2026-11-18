# AUTONOM Recruitment Agent Policy Integration

## Stage 25 of 50 — Multi-Agent Context Injection

---

### Specialist Agent Integration

The `RecruitmentPolicyAgentAdapter` provides a snapshot for specialist agents across the 24-agent swarm:

```python
snapshot = recruitment_policy_service.agent_adapter.get_agent_policy_snapshot()
```

#### Snapshot Payload Elements

- **`active_strategy`**:
  - Strategy ID and Title
  - Target role titles, families, and allowed seniority levels
  - Allowed work arrangements (remote/hybrid/onsite)
  - Target countries and excluded cities
  - Hard salary floor and undisclosed salary handling mode
- **`autonomy_mode`**: Active autonomy tier (`mode_1` through `mode_4`).
- **`remaining_daily_budget`**: Number of available application slots for today.
- **`blocked_employers_count`**: Number of companies on the hard blocklist.

---

### Action Permission Pre-Flight

Before an agent invokes an LLM tool or browser workflow:
```python
ok, msg = adapter.check_action_permission(agent_role="application_agent", action="submit_application")
if not ok:
    raise ActionProhibitedError(msg)
```
This guarantees that agent tasks fail fast with explicit policy reasons if an action exceeds permissions.
