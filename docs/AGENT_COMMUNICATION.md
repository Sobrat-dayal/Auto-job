# Inter-Agent Communication & Event Ledger (Stage 12)

## 1. Overview

AUTONOM coordinates multiple agents through typed, persistent messages rather than unstructured text chats. Every interaction across agents is logged to the `agent_messages` relational ledger.

---

## 2. Message Taxonomy

Messages adhere to 8 discrete types (`MessageType` enum):
1. `TASK_ASSIGNMENT`: Router dispatches a step to a capable agent, providing explainable routing details.
2. `TASK_RESULT`: Executing agent reports step completion, duration, and output summary back to the Supervisor.
3. `PROGRESS_UPDATE`: Executing agent reports partial progress or streaming chunks.
4. `VERIFICATION_REQUEST`: Supervisor requests the Verification Agent to audit step output against schema.
5. `VERIFICATION_RESULT`: Verification Agent returns pass/fail status, quality score, and evidence.
6. `ERROR_REPORT`: Executing agent reports failure or unexpected exception.
7. `RECOVERY_PROPOSAL`: Recovery Agent proposes retry, alternate model route, or dynamic replan.
8. `CAPABILITY_UNAVAILABLE`: Router reports that no eligible agent is available for a requested capability.

---

## 3. Persistent Schema (`agent_messages`)

```sql
CREATE TABLE agent_messages (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL REFERENCES workflows(id),
    sender_agent_id TEXT NOT NULL,
    recipient_agent_id TEXT NOT NULL,
    step_id TEXT REFERENCES workflow_steps(id),
    message_type TEXT NOT NULL,
    payload_json JSON NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

Clients and UI monitors query `/api/v1/orchestration/workflows/{workflow_id}/messages` to render real-time communication feeds.
