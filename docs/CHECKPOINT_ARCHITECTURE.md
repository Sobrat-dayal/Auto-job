# Checkpoint Architecture & Integrity Verification

## 1. Overview & Purpose

Workflows executing complex desktop tasks are prone to unexpected disruptions: application crashes, system reboots, network drops, OS notifications, or sudden window focus shifts. 

The Checkpoint Subsystem (`app/computer/workflow_reliability/checkpoints/`) establishes durable, lightweight, persistent recovery boundaries during workflow execution. Every checkpoint captures:
- Exact execution progress (completed step IDs, pending step IDs, variable bindings).
- Real-time environmental state fingerprints (active window, PID, URL, screen resolution).
- External side-effect ledger entries.
- SHA-256 cryptographic seal guaranteeing tamper evidence.

---

## 2. Checkpoint Data Model

Defined in `app/computer/workflow_reliability/contracts.py`:

```python
class CheckpointType(str, Enum):
    STEP_COMPLETION = "step_completion"
    SIDE_EFFECT_BOUNDARY = "side_effect_boundary"
    RECOVERY_POINT = "recovery_point"
    PERIODIC = "periodic"
    PRE_EXECUTION = "pre_execution"
    MANUAL = "manual"

class ExecutionCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid4().hex[:12]}")
    execution_id: str
    procedure_id: str
    step_index: int
    checkpoint_type: CheckpointType = CheckpointType.STEP_COMPLETION
    completed_steps: list[str] = Field(default_factory=list)
    state_fingerprint: str  # Hash of active window, process, URL, and viewport
    variable_bindings: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    integrity_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
```

---

## 3. State Fingerprinting Mechanism

A `state_fingerprint` represents a deterministic composite signature of the operating system and application environment at the moment of checkpoint creation:

```python
def capture_fingerprint(
    window_title: str | None = None,
    process_name: str | None = None,
    url: str | None = None,
    resolution: tuple[int, int] | None = None
) -> str:
    raw_payload = f"{window_title or ''}|{process_name or ''}|{url or ''}|{resolution or ''}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()[:16]
```

During crash recovery or resume planning, the current live desktop fingerprint is compared against the checkpoint's stored fingerprint. If they differ (e.g. the browser tab was closed or the app crashed), the recovery engine detects the environment mismatch and attempts application relaunch before step continuation.

---

## 4. SHA-256 Cryptographic Integrity Sealing

To prevent corrupted or forged checkpoints from being executed, each checkpoint is sealed using a cryptographic SHA-256 digest:

```python
def compute_checkpoint_hash(checkpoint: ExecutionCheckpoint) -> str:
    payload = (
        f"{checkpoint.checkpoint_id}:"
        f"{checkpoint.execution_id}:"
        f"{checkpoint.procedure_id}:"
        f"{checkpoint.step_index}:"
        f"{checkpoint.state_fingerprint}:"
        f"{sorted(checkpoint.completed_steps)}:"
        f"{sorted(checkpoint.variable_bindings.items())}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def seal_checkpoint(checkpoint: ExecutionCheckpoint) -> ExecutionCheckpoint:
    checkpoint.integrity_hash = compute_checkpoint_hash(checkpoint)
    return checkpoint

def verify_checkpoint(checkpoint: ExecutionCheckpoint) -> bool:
    expected = compute_checkpoint_hash(checkpoint)
    return hmac.compare_digest(checkpoint.integrity_hash, expected)
```

If `verify_checkpoint()` returns `False`, the checkpoint is rejected as compromised or corrupted, and the recovery reconciler falls back to the previous verified checkpoint.

---

## 5. Storage & Retention

Checkpoints are stored in the SQLite `execution_checkpoints` table with indexes on `(execution_id, step_index)`. Checkpoints are automatically pruned after 30 days unless marked with `preserve_evidence=True`.
