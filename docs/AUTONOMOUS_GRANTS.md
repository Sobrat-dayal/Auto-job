# AUTONOM Preauthorized Autonomy & Standing Grants

## 1. Concept of Bounded Autonomy

Requiring human confirmation for every trivial action impairs autonomy, while granting blanket permission compromises system safety. AUTONOM solves this through **Preauthorized Autonomy Grants** (`app.security.authorization.contracts.GrantDefinition`).

A grant is a cryptographically bound, temporary, bounded authorization that permits a specific agent or workflow to execute designated capabilities without repeated human prompts, provided all strict boundaries are satisfied:

```
                  ┌─────────────────────────────────────┐
                  │      Authorization Grant Check      │
                  └──────────────────┬──────────────────┘
                                     │
           ┌─────────────────────────┼────────────────────────┐
           ▼                         ▼                        ▼
     Time Limit               Max Uses Quota            Resource Scope
  (valid_until_dt)          (use_count < max)       (canonical root/origin)
           │                         │                        │
           └─────────────────────────┼────────────────────────┘
                                     ▼
                        [All Constraints Satisfied?]
                                     │
                        YES ─────────┴───────── NO
                         │                       │
                         ▼                       ▼
                   [AUTO-ALLOW]           [FALL THROUGH]
```

---

## 2. Grant Types

| Grant Type | Scope & Lifecycle | Use Case |
|---|---|---|
| `standing` | Long-lived until revoked or expired | Daily automated job scraping, background inbox triage |
| `workflow_scoped` | Bound strictly to one `workflow_id` | Full execution of a vetted recruitment pipeline |
| `task_scoped` | Bound strictly to a single `task_id` | One-off subtask delegation |
| `session_scoped` | Bound to active operator session (e.g. 1 hour) | Interactive coding or design iteration |

---

## 3. Grant Definition Schema

```json
{
  "id": "grant_daily_job_search",
  "name": "Daily Job Discovery Grant",
  "grant_type": "standing",
  "subject_type": "agent",
  "subject_id": "job_discovery_agent",
  "allowed_capabilities": ["recruitment_extract_job_requirements", "browser_navigate"],
  "resource_scope": {
    "allowed_origins": ["https://www.linkedin.com", "https://news.ycombinator.com"],
    "allowed_sources": ["greenhouse", "lever", "workday"]
  },
  "risk_limit": "moderate",
  "max_uses": 250,
  "use_count": 42,
  "valid_from": "2026-11-18T00:00:00Z",
  "valid_until": "2026-11-19T00:00:00Z",
  "is_revoked": false
}
```

---

## 4. Enforcement & Revocation

- **Usage Accounting**: Every successful execution under a grant increments `use_count`. If `use_count >= max_uses`, the grant automatically becomes inactive.
- **Expiration**: If `datetime.now(UTC) > valid_until`, the grant expires.
- **Immediate Revocation**: Calling `POST /api/v1/security/grants/{id}/revoke` sets `is_revoked = True` in SQLite and clears in-memory caches, instantaneously revoking permissions across all running agents.
