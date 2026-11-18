# Reusable Procedure Specification & Schema

## 1. Overview & Purpose

A `ReusableProcedure` is an immutable, versioned, parameterized workflow definition synthesized from one or more recorded sessions or authored directly. It represents a robust, deterministic computer-use program capable of running across environments, resolutions, and application restarts.

Unlike raw action recordings, a `ReusableProcedure`:
1. Replaces hardcoded values with declared typed parameters (`{{param_name}}`).
2. Defines explicit preconditions (window existence, active URL, focus state) and postconditions.
3. Specifies target re-resolution heuristics (CSS, UIA, OCR) with fallback tolerances.
4. Categorizes steps into idempotent versus non-idempotent operations for safe crash recovery.
5. Carries static risk scoring and authorization policy requirements.

---

## 2. Core Schema Definitions

All procedure contracts are declared using Pydantic V2 in `app/computer/workflow_reliability/contracts.py`:

```python
class ProcedureParameter(BaseModel):
    name: str
    parameter_type: str = "string"  # string, int, float, bool, secret
    description: str = ""
    default_value: Any = None
    required: bool = True
    is_secret: bool = False
    validation_regex: str | None = None

class StepAssertion(BaseModel):
    assertion_type: str  # element_exists, text_contains, url_matches, window_active
    target: InteractionTarget | None = None
    expected_value: Any = None
    timeout_ms: int = 5000

class ProcedureStep(BaseModel):
    step_id: str
    sequence: int
    name: str
    description: str = ""
    adapter: InteractionMethod
    action_type: str
    target: InteractionTarget
    parameters: dict[str, Any] = Field(default_factory=dict)
    timeout_ms: int = 10000
    retry_count: int = 2
    retry_backoff_ms: int = 500
    preconditions: list[StepAssertion] = Field(default_factory=list)
    postconditions: list[StepAssertion] = Field(default_factory=list)
    is_idempotent: bool = True
    risk_level: str = "low"  # low, medium, high, critical
    side_effect_category: str | None = None  # form_submission, payment, email_send

class ReusableProcedure(BaseModel):
    procedure_id: str
    name: str
    description: str = ""
    version: int = 1
    is_published: bool = False
    source_recording_id: str | None = None
    parameters: list[ProcedureParameter] = Field(default_factory=list)
    steps: list[ProcedureStep] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: datetime | None = None
    author: str = "system"
    risk_score: float = 0.0  # 0.0 to 100.0 computed statically
    metadata: dict[str, Any] = Field(default_factory=dict)
```

---

## 3. Parameter Interpolation & Template Syntax

Parameters are referenced inside step targets, URLs, values, and hotkeys using the mustache pattern: `{{parameter_name}}`.

Example step parameter dictionary:
```json
{
  "text": "Hello {{applicant_name}}, here is my resume for {{job_title}}.",
  "target_url": "https://company.careers.com/jobs/{{job_id}}"
}
```

During execution, the `ProcedureExecutor` resolves each placeholder against supplied execution inputs. If a required parameter is missing or fails regex validation, execution is halted prior to dispatching any actions.

---

## 4. Immutability & Versioning Semantics

To ensure reproducible runs and prevent silent workflow drift:
1. **Draft vs Published**: When a procedure is authored or compiled, it starts as `is_published = False`. It can be edited, reordered, and validated.
2. **Immutable Publication**: Once `publish_version()` is called, the procedure is frozen. Any subsequent edits create a new draft incrementing `version = version + 1`.
3. **Execution Integrity**: Replay executions always reference a specific immutable version, ensuring audit logs and checkpoints match exact execution steps.
