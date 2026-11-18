# Stage 19: Unified Action Contracts & Execution Lifecycle

## 1. Unified Action Definition (`InteractionAction`)

AUTONOM provides a single normalized schema for all computer operations across browser, desktop, and visual surfaces:

```python
class HybridActionType(str, Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    ENTER_TEXT = "enter_text"
    NAVIGATE = "navigate"
    SCROLL = "scroll"
    KEY_PRESS = "key_press"
    HOTKEY = "hotkey"
    INSPECT = "inspect"
    SUBMIT = "submit"
    SELECT_OPTION = "select_option"

class ActionRiskLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    REPEATABLE = "REPEATABLE"
    CONDITIONALLY_REPEATABLE = "CONDITIONALLY_REPEATABLE"
    NON_IDEMPOTENT = "NON_IDEMPOTENT"
    IRREVERSIBLE = "IRREVERSIBLE"

class InteractionAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    task_id: Optional[str] = None
    target: InteractionTarget
    action_type: HybridActionType
    method: Optional[InteractionMethod] = None  # None = Engine auto-routes

    # Payload parameters
    input_text: Optional[str] = None
    key: Optional[str] = None
    hotkey_modifiers: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    click_offset: Optional[Dict[str, float]] = None

    # Safety and Idempotency flags
    risk_level: ActionRiskLevel = ActionRiskLevel.REPEATABLE
    is_non_idempotent: bool = False
    expected_mutation: Optional[str] = None
    timeout_ms: int = 15000
    allow_fallback: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 2. Execution Result Contract (`InteractionResult`)

```python
class HybridVerificationStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN_OUTCOME = "unknown_outcome"
    NOT_VERIFIED = "not_verified"

class InteractionResult(BaseModel):
    action_id: str
    method: InteractionMethod
    success: bool
    execution_time_ms: float
    verification_status: HybridVerificationStatus
    verification_details: str
    error_message: Optional[str] = None
    mutation_detected: bool = False
    fallback_occurred: bool = False
    fallback_attempts: int = 0
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 3. Finite State Machine Lifecycle (`HybridStateMachine`)

The execution of a hybrid task transitions deterministically through a finite set of states:

```
PENDING ---> ROUTING ---> EXECUTING ---> VERIFYING ---> COMPLETED
                |              |              |
                |              v              v
                +--------> FALLING_BACK ------+
                               |
                               v
                             FAILED (or BLOCKED_POLICY)
```

State transitions are guarded against illegal jumps (e.g. attempting to jump from `COMPLETED` back to `EXECUTING` raises `StateTransitionError`).
