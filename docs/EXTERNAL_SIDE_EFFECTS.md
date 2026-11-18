# External Side-Effects & Idempotency Ledger

## 1. Overview & Problem Statement

In autonomous computer automation, operations fall into two fundamental classes:
1. **Idempotent Operations**: Actions that can be safely repeated without altering state (e.g. focusing a window, scrolling a document, reading text, navigating to a read-only URL).
2. **Non-Idempotent Operations**: Actions that produce external real-world side effects (e.g. submitting a job application form, clicking a payment button, sending an email, modifying a database).

If a crash or network interruption occurs while executing a non-idempotent action, naive retries run the risk of **duplicate job submissions**, **double charges**, or **repeated messages**.

The External Side-Effects Ledger (`app/computer/workflow_reliability/recovery/side_effects.py` & `idempotency.py`) provides an authoritative, persistent record of non-idempotent operations to prevent duplicate execution during recovery.

---

## 2. Action Idempotency Classification

The engine evaluates actions before execution using deterministic rules:

```python
NON_IDEMPOTENT_PATTERNS = {
    "submit", "pay", "order", "send", "delete", "post", "apply", "checkout", "transfer"
}

def classify_action(action_type: str, target: InteractionTarget, parameters: dict[str, Any]) -> bool:
    # Returns True if idempotent, False if non-idempotent
    text_content = (target.text or "").lower()
    selector = (target.selector or "").lower()
    
    for pattern in NON_IDEMPOTENT_PATTERNS:
        if pattern in action_type.lower() or pattern in text_content or pattern in selector:
            return False
    return True
```

---

## 3. Intent Hashing & Ledger Entries

Before a non-idempotent action is dispatched to an adapter:
1. An **Intent Hash** is computed across the procedure ID, step sequence, target identity, and interpolated parameters:
   $$\text{IntentHash} = \text{SHA-256}(\text{procedure\_id} \,\|\, \text{step\_id} \,\|\, \text{target} \,\|\, \text{parameters})$$
2. The ledger records a `SideEffectRecord` with status `PENDING`.
3. The action executes.
4. If successful, status transitions to `CONFIRMED`. If failed, transitions to `FAILED` or `UNCERTAIN`.

```python
class SideEffectRecord(BaseModel):
    effect_id: str = Field(default_factory=lambda: f"eff_{uuid4().hex[:12]}")
    execution_id: str
    procedure_id: str
    step_id: str
    intent_hash: str
    action_type: str
    target_summary: str
    status: SideEffectOutcome  # PENDING, CONFIRMED, FAILED, UNCERTAIN
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evidence: dict[str, Any] = Field(default_factory=dict)
```

---

## 4. Duplicate Operation Prevention During Replay / Recovery

When a procedure resumes from an interrupted state:
1. The `ResumePlanner` inspects the side-effect ledger for every candidate resume step.
2. If an intent hash for a non-idempotent step is marked `CONFIRMED`, that step is **marked already completed and skipped**.
3. If an intent hash is marked `UNCERTAIN` (e.g. the network timed out right as the submit button was clicked), automated retry is **blocked**. The engine creates an escalation request requiring user confirmation before proceeding.

This eliminates accidental duplicate submissions during network retries or process crashes.
