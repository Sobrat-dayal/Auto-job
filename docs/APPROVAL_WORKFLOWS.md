# AUTONOM Human-in-the-Loop Approval Workflows

## 1. Approval Architecture

When an autonomous agent attempts an action that requires human sign-off (due to high risk or policy rules), the `ToolExecutionGateway` halts the action and submits an `ApprovalRequest` to the persistent SQLite queue (`approval_requests`).

```
 Agent Execution ──► ToolExecutionGateway ──► Engine.evaluate() ──► REQUIRE_APPROVAL
                            │
                            ▼
                  ApprovalManager.create_or_get_request()
                            │
                   [Deduplication via SHA-256 Digest]
                            │
                            ▼
                 Approval Queue (`/approvals`)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
       User Approves                   User Denies
            │                               │
            ▼                               ▼
     status='approved'               status='denied'
            │                               │
            ▼                               ▼
   Workflow Resumes Step             Step Fails / Aborts
            │
            ▼
     Gateway Consumes
     status='consumed'
```

---

## 2. Cryptographic Deduplication

To prevent flooding the operator with duplicate requests during retries:
1. The engine calculates `parameters_digest = sha256(json(capability, action, params, scope))`.
2. `ApprovalManager.create_or_get_request` queries SQLite for any existing `pending` request with identical digest, workflow ID, and step ID.
3. If found, returns the existing approval ID without creating duplicate noise in the operator UI.

---

## 3. Approval Modes

When granting approval, the operator can choose the scope of authorization:
- `one_time`: The approval applies to this single tool execution only. Once executed, the status transitions to `consumed` and cannot be replayed.
- `session`: The engine creates an ephemeral 1-hour grant for this action and subject.
- `workflow`: Authorizes this action for the remainder of this specific workflow run.
- `standing_grant`: Promotes the approval into a standing grant with an operator-defined expiration and usage limit.

---

## 4. Replay Attack Prevention

If an attacker or prompt injection attempts to replay an approved request ID with altered arguments:
1. The parameter digest of the new call will not match the approved record's digest.
2. The approved record's single-use `status` is already `consumed`.
3. The engine rejects the action and forces a fresh approval request with the new parameter payload.
