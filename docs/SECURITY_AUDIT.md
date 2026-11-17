# AUTONOM Security & Authorization Audit Ledger

## 1. Append-Only Audit Ledger

All authorization decisions rendered by the Authorization Engine are persisted in the `authorization_decisions` table in SQLite. This ledger provides cryptographic and procedural provenance for every autonomous operation:

```sql
CREATE TABLE authorization_decisions (
    id VARCHAR(64) PRIMARY KEY,
    correlation_id VARCHAR(64) NULL,
    actor_id VARCHAR(64) NOT NULL,
    actor_type VARCHAR(32) NOT NULL,
    agent_id VARCHAR(64) NULL,
    workflow_id VARCHAR(64) NULL,
    step_id VARCHAR(64) NULL,
    capability_id VARCHAR(128) NOT NULL,
    action VARCHAR(128) NOT NULL,
    parameters_digest VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id VARCHAR(128) NULL,
    outcome VARCHAR(32) NOT NULL,
    policy_id VARCHAR(64) NULL,
    grant_id VARCHAR(64) NULL,
    reason_code VARCHAR(64) NOT NULL,
    explanation TEXT NOT NULL,
    risk_level VARCHAR(32) NOT NULL,
    timestamp DATETIME NOT NULL
);
```

---

## 2. Decision Querying & Telemetry

Operators can inspect and filter audit trails via:
- REST API: `GET /api/v1/security/audit?limit=50&outcome=deny`
- Frontend: Approvals Workspace $\rightarrow$ **Audit Ledger** tab.
- Correlation IDs: Trace an entire multi-agent workflow tree using `correlation_id`.
