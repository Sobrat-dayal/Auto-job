# AUTONOM — Agent Security, Context Isolation, & Safety Boundaries

## 1. Threat Model & Security Posture

AUTONOM coordinates autonomous agents capable of analyzing complex files, processing recruiter communications, and planning computer workflows. This surface introduces critical security vectors:

1. **Prompt Injection Escalation**: An untrusted external input (e.g., a malicious job posting or crafted email) attempting to hijack an agent into extracting sensitive user secrets.
2. **Credential Leakage**: Unintended propagation of DPAPI-encrypted API keys, database credentials, or auth tokens to specialist agents or external LLM inference endpoints.
3. **Runaway Resource Consumption**: Malicious or recursive tasks exhausting system memory, GPU VRAM, or client rate limits.
4. **Unauthorized Desktop Injection**: Unreviewed agent commands triggering dangerous Win32 operations.

---

## 2. Context Isolation Architecture

Every agent enforces boundary checks via `AgentContextPolicy` within the `SpecialistAgent` base class:

```python
class AgentContextPolicy(BaseModel):
    allow_credentials: bool = False
    allow_personal_data: bool = True
    allowed_context_keys: List[str] = Field(default_factory=list)
    sanitize_inputs: bool = True
```

### Context Enforcement Protocol

```
[Inbound AgentRequest]
         |
         v
+---------------------------------------+
|  SpecialistAgent.validate_input()     |
+-------------------+-------------------+
                    |
      Is allow_credentials == False?
                    |
         +----------+----------+
         | Yes                 | No (Only allowed for Core Orchestration)
         v                     v
+-------------------+    +--------------------+
| Scan all keys for |    | Skip credential    |
| sensitive terms   |    | term rejection     |
| (api_key, secret, |    +--------------------+
| password, token)  |
+---------+---------+
          |
    Sensitive key found?
          |
    +-----+-----+
    |           |
   Yes          No
    |           |
    v           v
[ABORT EXECUTION]  [Forward Sanitized Context to Agent]
- Status: FAILED
- Error: SecurityViolation
```

---

## 3. Strict Validation Invariant

During agent registration, `validate_manifest()` in `services/api/app/orchestration/agents/manifests.py` strictly prevents misconfiguration:

```python
if manifest.category != AgentCategory.ORCHESTRATION and manifest.context_policy.allow_credentials:
    raise ValueError(f"Specialist agent '{manifest.id}' cannot have allow_credentials=True")
```

This ensures that even if a developer or dynamic configuration update requests credential access for a specialist agent, the registry permanently denies it.

---

## 4. Hardware Safety & Resource Isolation

| Defense Layer | Mechanism | Protection Target |
|---|---|---|
| **GPU VRAM** | `asyncio.Semaphore(1)` in `AIGateway` | Prevents OOM crashes on RTX 4050 6GB Laptop GPU |
| **Execution Timeouts** | `asyncio.wait_for(timeout=max_seconds)` | Prevents hung processes and infinite loops |
| **Max Output Tokens** | Clamped at 4,096 tokens | Prevents token-overflow memory exhaustion |
| **Retry Caps** | Maximum 5 retries (default 2) | Prevents infinite retry storms on deterministic failures |
| **Audit Trails** | SQLite `agent_executions` table | Full traceability of all agent invocations, tokens, and errors |

---

## 5. Security Testing Verification

The framework's security boundaries were verified via automated unit and integration tests in `services/api/tests/test_specialist_collaboration.py`:
- `test_context_isolation_credential_rejection`: Successfully verifies that sending an input dictionary with `api_key` or `password` to `JobMatchingAgent` or any specialist immediately aborts with `AgentStatus.FAILED` and an explicit security message.
- `test_disabled_agent_behavior`: Confirms that setting `is_active=False` causes immediate execution rejection without any capability invocation.
- `test_agent_manifest_validation`: Confirms that setting `allow_credentials=True` on a non-orchestration agent throws a `ValueError`.
