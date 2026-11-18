# Autonomous Computer Crash Recovery & Resume Planning

## 1. Overview & Objectives

Autonomous desktop workflows must survive unexpected interruptions: application crashes, system restarts, focus loss, network timeouts, or process terminations.

The Recovery Subsystem (`app/computer/workflow_reliability/recovery/`) provides automated, intelligent recovery and resumption:
1. **Crash Reconciliation**: Discovers orphaned or interrupted executions on startup.
2. **Failure Classification**: Distinguishes transient network errors from permanent structural breaks.
3. **Resume Planning**: Synthesizes a safe continuation plan from the latest valid checkpoint, skipping confirmed side-effects and validating preconditions.

---

## 2. Recovery Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                      APPLICATION STARTUP / RESTORE                                 |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                               CRASH RECONCILER (`reconciler.py`)                                   |
| - Scan `executions` table for status in `['running', 'initializing']`                              |
| - Inspect OS process table: is target application process still alive?                             |
| - Fetch latest valid checkpoint with verified cryptographic SHA-256 seal                           |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                              FAILURE CLASSIFIER (`classifier.py`)                                  |
| - Classify interruption into taxonomy:                                                             |
|   * APP_CRASH: Target process vanished                                                             |
|   * FOCUS_LOST: Target window obscured or unfocused                                                |
|   * TIMEOUT: Operation exceeded deadline                                                           |
|   * ELEMENT_NOT_FOUND: Structural UI changed                                                       |
|   * UNKNOWN_ABORT: System restart or power loss                                                    |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                              RESUME PLANNER (`resume_planner.py`)                                  |
| - Determine remaining steps: `all_steps - completed_steps`                                         |
| - Audit external side-effects ledger (skip confirmed non-idempotent steps)                         |
| - Verify environment prerequisites (launch app if crashed, restore focus)                          |
| - Produce executable `RecoveryPlan`                                                                |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                   SAFE RESUME DISPATCH / USER APPROVAL                             |
| - Safe to resume: Dispatch continuation via `ProcedureExecutor`                                   |
| - Ambiguous state: Prompt user with Recovery Plan via Desktop UI                                   |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Failure Classification Taxonomy

Failures are categorized into discrete recovery classifications:

```python
class RecoveryClassification(str, Enum):
    SAFE_TO_RETRY = "safe_to_resume"       # Idempotent step or pre-execution failure
    ENVIRONMENT_MISMATCH = "environment_mismatch" # Target app closed, needs relaunch
    SIDE_EFFECT_UNCERTAIN = "side_effect_uncertain" # Non-idempotent step interrupted mid-flight
    STRUCTURAL_CHANGE = "structural_change" # UI element missing or changed
    FATAL_ERROR = "fatal_error"             # Permission denied or invalid parameter
```

---

## 4. Resume Planning & Continuation

The `ResumePlanner` calculates the exact set of steps required to complete the procedure:

```python
def plan_resume(
    execution_id: str,
    procedure: ReusableProcedure,
    checkpoint: ExecutionCheckpoint,
    confirmed_effects: list[str]
) -> RecoveryPlan:
    completed_ids = set(checkpoint.completed_steps)
    steps_to_run = []
    skipped_steps = []
    
    for step in procedure.steps:
        if step.step_id in completed_ids:
            skipped_steps.append(step.step_id)
            continue
        if step.step_id in confirmed_effects:
            # Confirmed in external side-effects ledger
            skipped_steps.append(step.step_id)
            continue
        steps_to_run.append(step)
        
    return RecoveryPlan(
        execution_id=execution_id,
        procedure_id=procedure.procedure_id,
        checkpoint_id=checkpoint.checkpoint_id,
        classification=RecoveryClassification.SAFE_TO_RETRY,
        steps_to_execute=[s.step_id for s in steps_to_run],
        steps_skipped=skipped_steps,
        can_resume=True
    )
```

---

## 5. Endpoints & UI Integration

Interrupted workflows and their recovery plans are exposed via:
- `GET /api/v1/reliability/executions/{execution_id}/recovery-plan`: Retrieves generated recovery plan.
- `POST /api/v1/reliability/executions/{execution_id}/resume`: Executes recovery plan with optional overridden parameters.
- Frontend: Managed through the `RecoveryCenterTab.tsx` UI workspace.
