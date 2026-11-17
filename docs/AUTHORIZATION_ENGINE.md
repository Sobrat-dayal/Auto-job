# AUTONOM Authorization Engine Architecture

## 1. Executive Summary

Stage 14 of AUTONOM introduces a centralized, deterministic, fail-closed **Authorization Engine** (`app.security.authorization.engine.AuthorizationEngine`). Unlike cosmetic UI checks or LLM prompt-level guardrails, the Authorization Engine sits directly at the backend capability execution boundary. Every agent invocation, automated tool call, network transmission, and filesystem mutation passes through this engine prior to execution.

```
                  ┌─────────────────────────────────────┐
                  │        Incoming Tool Request        │
                  │   (ActorContext, Capability, Params)│
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 1. Global Emergency Stop Active?    │─── YES ───► [DENY: EMERGENCY_STOP_ENGAGED]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 2. Automation Dispatch Paused?      │─── YES ───► [DENY: AUTOMATION_PAUSED]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 3. Credential Invariant Check       │─── VIOLATION ───► [DENY: CREDENTIAL_ACCESS_RESTRICTED]
                  └──────────────────┬──────────────────┘
                                     │ OK
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 4. Pre-Existing Approved Request?   │─── MATCH ───► [ALLOW: APPROVAL_GRANTED]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 5. Active Standing / Workflow Grant?│─── MATCH ───► [ALLOW: PREAUTHORIZED_GRANT]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 6a. Explicit Deny Policies          │─── MATCH ───► [DENY: EXPLICIT_DENY_POLICY]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 6b. Require Approval Policies       │─── MATCH ───► [REQUIRE_APPROVAL: APPROVAL_REQUIRED_BY_POLICY]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 6c. Explicit Allow Policies         │─── MATCH ───► [ALLOW: EXPLICIT_ALLOW_POLICY]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 7. Low-Risk Safe Read Baseline      │─── LOW RISK ───► [ALLOW: READ_ONLY_BASELINE]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 8. High / Critical Action Guard     │─── HIGH/CRIT ───► [REQUIRE_APPROVAL: HIGH_RISK_ACTION]
                  └──────────────────┬──────────────────┘
                                     │ NO
                                     ▼
                                [DEFAULT DENY]
```

---

## 2. Deterministic Evaluation Precedence

The engine evaluates authorization requests strictly in the following precedence order:

1. **Global Emergency Stop**: Overrides all other policies, grants, and approvals. If active, execution is immediately rejected with reason code `EMERGENCY_STOP_ENGAGED`.
2. **Automation Pause**: If automation dispatch is paused and the actor is an autonomous agent, dispatch is blocked with `AUTOMATION_PAUSED`.
3. **Hard Security Invariants**: Hardcoded invariants that can never be relaxed by custom policies or grants:
   - Specialist agents can never read raw cryptographic credentials or secrets (`CREDENTIAL_ACCESS_RESTRICTED`).
   - Actions classified as `CRITICAL` can never be executed without explicit operator intervention or valid grant.
4. **Pre-Existing Approval Match**: Evaluates whether an unconsumed, non-expired human approval exists in SQLite with an identical parameter digest (`APPROVAL_GRANTED`).
5. **Preauthorized Autonomy Grants**: Evaluates active standing grants, workflow-scoped grants, or task grants. If valid, non-expired, and within usage limits, grants `PREAUTHORIZED_GRANT`.
6. **Policy Evaluation**:
   - **6a. Explicit Deny Rules**: If any active policy explicitly denies the action or scope, returns `EXPLICIT_DENY_POLICY`.
   - **6b. Require Approval Rules**: If any policy mandates human approval, returns `REQUIRE_APPROVAL`.
   - **6c. Explicit Allow Rules**: If a policy explicitly permits the action within scope, returns `EXPLICIT_ALLOW_POLICY`.
7. **Low-Risk Read-Only Baseline**: Low-risk operations (e.g., text parsing, skill matching, static code review) default to `ALLOW` (`READ_ONLY_BASELINE`).
8. **High-Risk Action Guard**: Any ungranted action classified as `HIGH` or `CRITICAL` risk automatically escalates to `REQUIRE_APPROVAL` (`HIGH_RISK_ACTION`).
9. **Fail-Closed Default Deny**: If no matching rule or baseline authorizes the action, it is blocked with `DEFAULT_DENY`.

---

## 3. Cryptographic Parameter Digests & Replay Defense

Every authorization request calculates a deterministic SHA-256 parameter digest:
```python
def compute_digest(self) -> str:
    raw = json.dumps(
        {
            "capability_id": self.capability_id,
            "action": self.action,
            "parameters": self.parameters,
            "resource_scope": self.resource_scope,
        },
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

### Single-Use Consumption (`consumed` state)
Approvals are single-use by default. When a tool completes execution, the `ToolExecutionGateway` marks the approval request status as `consumed`:
- Attempting to replay the exact same action without re-authorization will fail because the request is no longer `approved`.
- If parameters are altered (e.g., different destination email, modified file path), the SHA-256 digest changes, immediately invalidating the previous approval.

---

## 4. Reason Codes

All authorization decisions record a standardized reason code in the append-only SQLite audit ledger:

| Reason Code | Effect | Description |
|---|---|---|
| `EMERGENCY_STOP_ENGAGED` | `DENY` | Global emergency stop is active. |
| `AUTOMATION_PAUSED` | `DENY` | Autonomous task dispatch is paused by operator. |
| `CREDENTIAL_ACCESS_RESTRICTED` | `DENY` | Security invariant: direct raw credential read blocked. |
| `SECURITY_INVARIANT_VIOLATION` | `DENY` | Violation of kernel safety invariant. |
| `EXPLICIT_DENY_POLICY` | `DENY` | Operation forbidden by an active policy rule. |
| `APPROVAL_REQUIRED_BY_POLICY` | `REQUIRE_APPROVAL` | Mandatory human sign-off enforced by policy. |
| `EXPLICIT_ALLOW_POLICY` | `ALLOW` | Operation permitted by enabled policy rule. |
| `PREAUTHORIZED_GRANT` | `ALLOW` | Authorized under bounded active standing grant. |
| `APPROVAL_GRANTED` | `ALLOW` | Authorized via explicit human operator approval. |
| `HIGH_RISK_ACTION` | `REQUIRE_APPROVAL` | High/critical operation escalates to approval. |
| `READ_ONLY_BASELINE` | `ALLOW` | Low-risk analytical safe read operation. |
| `DEFAULT_DENY` | `DENY` | Fail-closed deny: no rule permitted operation. |
