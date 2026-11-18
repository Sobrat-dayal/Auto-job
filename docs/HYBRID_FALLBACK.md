# Stage 19: Context-Aware Fallback & Recovery Engine

## 1. Principles of Safe Fallback

Automatic fallback between control methods is essential when automating complex applications, but unconstrained fallback can cause catastrophic errors. AUTONOM enforces five mandatory safety rules for fallback execution:

1. **Strictly Bounded Depth:** Maximum 3 method switches per action. Exceeding this limit immediately raises `FallbackLimitExceededError`.
2. **No Infinite Loops:** An action cannot fall back to a method that has already been attempted during that action's lifecycle.
3. **Non-Idempotent Action Guard:** Actions classified as `NON_IDEMPOTENT` or `IRREVERSIBLE` (e.g. submitting payments, finalizing application forms, sending emails) cannot fall back if the initial attempt returned an uncertain outcome (`unknown_outcome`). Replaying a non-idempotent action on an uncertain state would risk duplicate submissions.
4. **Re-observation Before Fallback:** Before invoking the secondary adapter, the coordinator re-observes the target to ensure the window has not closed, the DOM has not mutated, or the focus has not shifted.
5. **Authorization Re-evaluation:** Fallback candidates must be evaluated against the Stage 14 policy engine. A fallback method cannot bypass permissions or execute an unapproved privileged action.

---

## 2. Fallback Controller Architecture (`routing/fallback.py`)

```python
class FallbackController:
    def __init__(self, max_fallback_steps: int = 3) -> None:
        self.max_fallback_steps = max_fallback_steps

    def validate_fallback_eligibility(
        self,
        action: InteractionAction,
        initial_method: InteractionMethod,
        fallback_method: InteractionMethod,
        attempted_methods: List[InteractionMethod],
        verification_status: HybridVerificationStatus,
    ) -> None:
        # Check 1: Fallback permitted by caller
        if not action.allow_fallback:
            raise FallbackBlockedError("Fallback disallowed for this action.")

        # Check 2: Max attempts threshold
        if len(attempted_methods) >= self.max_fallback_steps:
            raise FallbackLimitExceededError(f"Exceeded max fallback attempts ({self.max_fallback_steps}).")

        # Check 3: Unique candidate
        if fallback_method in attempted_methods:
            raise FallbackBlockedError(f"Method {fallback_method} already attempted.")

        # Check 4: Idempotency safety on uncertain outcome
        if action.is_non_idempotent and verification_status == HybridVerificationStatus.UNKNOWN_OUTCOME:
            raise NonIdempotentActionBlockedError(
                f"Cannot fall back to {fallback_method}: action is non-idempotent and outcome is uncertain."
            )
```

---

## 3. Fallback Audit Trail (`FallbackRecordSchema`)

Whenever a fallback occurs, a `FallbackRecordSchema` is logged in the task attempt history:
- `fallback_id`: Trace identifier (`fb_...`).
- `task_id`: Linked task ID.
- `initial_method`: The adapter that failed or timed out.
- `fallback_method`: The secondary adapter selected.
- `trigger_reason`: Detailed failure reason from the initial adapter.
- `reobservation_successful`: Boolean indicating whether pre-fallback re-observation succeeded.
- `outcome`: Final outcome of the fallback attempt.
