# AUTONOM — Agent Manifest Specification

## 1. Specification Overview

Every agent in AUTONOM is governed by an **Agent Manifest** (`AgentManifest`), a strongly typed configuration contract defined in `services/api/app/orchestration/agents/contracts.py`.

Manifests declare an agent's identity, role, functional capabilities, model preferences, context isolation boundaries, execution timeouts, and retry policies.

---

## 2. Pydantic Schema Definition

```python
class AgentCategory(str, Enum):
    ORCHESTRATION = "orchestration"
    RECRUITMENT = "recruitment"
    COMPUTER = "computer"
    CODING = "coding"
    RESEARCH = "research"
    PRODUCTIVITY = "productivity"
    CREATIVE = "creative"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"

class AvailabilityState(str, Enum):
    OPERATIONAL = "operational"
    LIMITED = "limited"
    PLANNED = "planned"

class AgentModelProfile(BaseModel):
    preferred_local_model: str = "qwen2.5:7b"
    preferred_cloud_model: str = "gemini-1.5-flash"
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    max_output_tokens: int = Field(2048, ge=128, le=8192)
    reasoning_effort: str = "standard"  # low, standard, high
    fallback_model: Optional[str] = None

class AgentContextPolicy(BaseModel):
    allow_credentials: bool = False
    allow_personal_data: bool = True
    allowed_context_keys: List[str] = Field(default_factory=list)
    sanitize_inputs: bool = True

class AgentExecutionLimits(BaseModel):
    max_execution_time_seconds: int = Field(120, ge=5, le=600)
    max_retries: int = Field(2, ge=0, le=5)
    supports_cancellation: bool = True

class AgentManifest(BaseModel):
    id: str
    name: str
    category: AgentCategory
    description: str
    availability: AvailabilityState = AvailabilityState.OPERATIONAL
    is_active: bool = True
    capabilities: List[str] = Field(default_factory=list)
    model_profile: AgentModelProfile = Field(default_factory=AgentModelProfile)
    context_policy: AgentContextPolicy = Field(default_factory=AgentContextPolicy)
    execution_limits: AgentExecutionLimits = Field(default_factory=AgentExecutionLimits)
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
```

---

## 3. Strict Validation Rules

The `validate_manifest(manifest: AgentManifest)` function enforces invariant safety rules:

1. **Identifier Format**:
   - `id` must be lowercase alphanumeric with underscores only (`^[a-z0-9_]+$`).
2. **Credential Safety Invariant**:
   - Specialist agents (`category != AgentCategory.ORCHESTRATION`) **MUST NOT** have `allow_credentials = True`.
   - Attempting to register a specialist agent with `allow_credentials = True` raises a validation error.
3. **Capability Registration**:
   - Every string in `manifest.capabilities` must correspond to a valid capability format (`domain_action_target`).
4. **Execution Limits**:
   - `max_execution_time_seconds` must fall between 5 and 600 seconds.
   - `max_retries` cannot exceed 5.

---

## 4. Example Manifest: Resume Tailoring Agent

```json
{
  "id": "resume_agent",
  "name": "Resume & Tailoring Agent",
  "category": "recruitment",
  "description": "Aligns verified candidate skills and achievements with target job requirements.",
  "availability": "operational",
  "is_active": true,
  "capabilities": [
    "recruitment_draft_resume_bullets",
    "recruitment_match_skills"
  ],
  "model_profile": {
    "preferred_local_model": "qwen2.5:7b",
    "preferred_cloud_model": "gemini-1.5-flash",
    "temperature": 0.2,
    "max_output_tokens": 3072,
    "reasoning_effort": "high",
    "fallback_model": "mistral:7b"
  },
  "context_policy": {
    "allow_credentials": false,
    "allow_personal_data": true,
    "allowed_context_keys": ["profile", "job", "analysis", "skills"],
    "sanitize_inputs": true
  },
  "execution_limits": {
    "max_execution_time_seconds": 180,
    "max_retries": 2,
    "supports_cancellation": true
  },
  "tags": ["recruitment", "resume", "tailoring", "latex"],
  "version": "1.0.0"
}
```

---

## 5. Dynamic Configuration Updates

Through the REST API (`PATCH /api/v1/agents/{id}/configuration`), users and supervisors can customize an agent's active state, model preferences, and execution limits at runtime without restarting the application:

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/agents/resume_agent/configuration \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": true,
    "model_profile": {
      "temperature": 0.15,
      "max_output_tokens": 4096
    },
    "execution_limits": {
      "max_execution_time_seconds": 240
    }
  }'
```

All updates are validated and persisted in the SQLite `agent_configurations` table.
