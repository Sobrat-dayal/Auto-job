# AUTONOM — Specialist AI Agent Framework Architecture

## 1. Executive Overview

Stage 13 establishes the **Specialist AI Agent Framework** for AUTONOM. Building upon Stage 11 (Unified AI Model Gateway) and Stage 12 (Multi-Agent Orchestration & Supervisor Runtime), this framework provides an extensible, strongly typed, and secure foundation for running 24 distinct autonomous agent roles.

The framework enforces strict lifecycle phases, model profile matching, context isolation boundaries, execution timeouts, hardware safety guardrails (preventing VRAM thrashing on RTX 4050 6GB), and cooperative task verification and recovery.

```
       +-------------------------------------------------------+
       |                  Supervisor Agent                     |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |               Planner & DAG Scheduler                 |
       +---------------------------+---------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
|                      Specialist Agent Framework                     |
|                                                                     |
|  +--------------------+  +--------------------+  +---------------+  |
|  | Context Isolation  |  | Execution Envelope |  | Model Profile |  |
|  | Sensitive Sanitizer|  | Limits & Deadlines |  | & AI Gateway  |  |
|  +---------+----------+  +---------+----------+  +-------+-------+  |
|            |                       |                     |          |
|            +-----------------------+---------------------+          |
|                                    |                                |
|                                    v                                |
|  +---------------------------------------------------------------+  |
|  |              Specialist Execution Base Class                  |  |
|  |                     (SpecialistAgent)                         |  |
|  +---------------------------------+-----------------------------+  |
|                                    |                                |
|         +--------------------------+--------------------------+     |
|         v                          v                          v     |
|  +--------------+          +---------------+          +-----------+ |
|  | Capabilities |          | AI Gateway    |          | Database  | |
|  | Handlers (32)|          | LLM Inference |          | Artifacts | |
|  +--------------+          +---------------+          +-----------+ |
+------------------------------------+--------------------------------+
                                     |
                                     v
       +-------------------------------------------------------+
       |             Verification & Recovery Loop              |
       +-------------------------------------------------------+
```

---

## 2. Core Framework Principles

1. **Zero-Fake Capabilities & Honest Availability**:
   Agents declare their true availability status (`operational`, `limited`, `planned`). Capabilities requiring future integrations (e.g., live job board submission, external email SMTP/IMAP sending, Windows UI injection) are not falsified. Instead, structured drafts, simulated analysis, and explicit pre-conditions are provided.
2. **Strict Context Isolation**:
   Specialist agents only receive data declared in their `AgentContextPolicy`. Any payload containing credentials, raw authentication tokens, or master passwords is automatically rejected at the agent boundary, preventing prompt injection privilege escalation.
3. **Hardware-Aware Model Profiles**:
   Every agent declares preferred local and cloud models, temperature, reasoning effort, and token limits. In accordance with the RTX 4050 Laptop GPU guardrail, all LLM-backed calls funnel through the AI Gateway's single-active-model semaphore (`asyncio.Semaphore(1)`), preventing out-of-memory errors.
4. **Contract-Driven Capability Dispatching**:
   Specialist agents inherit from `SpecialistAgent` and map orchestration tasks to granular, validated capability functions registered in `CapabilityRegistry`.
5. **Durable Telemetry & Auditability**:
   Every agent invocation records execution latency, status, output token estimations, and error traces, persisted in SQLite for historical analytics.

---

## 3. Class Hierarchy & Architecture

```
services/api/app/orchestration/agents/
├── contracts.py       # Pydantic schemas (AgentManifest, AgentModelProfile, etc.)
├── base.py            # SpecialistAgent base class with lifecycle & isolation
├── manifests.py       # Default manifests catalog for all 24 agents
├── registry.py        # AgentRegistry singleton with validation & telemetry
└── specialists/       # Concrete specialist implementations
    ├── recruitment.py # JobDiscovery, JobMatching, Resume, Application, Comms, Interview
    ├── coding.py      # CodingAgent
    ├── research.py    # ResearchAgent, MarketIntelligenceAgent
    ├── productivity.py# DocumentAgent, SpreadsheetAgent, PresentationAgent
    ├── creative_comms.py # CreativeAgent, MessagingAgent
    ├── automation.py  # WorkflowAutomationAgent
    └── computer.py    # BrowserAgent, WindowsComputerAgent, VisualGrounding, StructuralUI
```

### 3.1 `SpecialistAgent` Base Class

The `SpecialistAgent` class standardizes the lifecycle of every specialist agent:

```python
class SpecialistAgent:
    def __init__(self, manifest: AgentManifest, capability_registry: Optional[CapabilityRegistry] = None):
        self.manifest = manifest
        self.capabilities = capability_registry or get_capability_registry()

    async def execute_task(self, request: AgentRequest) -> AgentResult:
        # 1. State check (is_active)
        # 2. Context isolation & input validation
        # 3. Execution limits (timeout & cancellation)
        # 4. Capability dispatch or custom logic
        # 5. Result construction & handoff proposal
```

### 3.2 Context Isolation Mechanics

When `validate_input(request)` is executed:
- If `allow_credentials` is `False`, the agent inspects the input parameters for forbidden keys (`api_key`, `credentials`, `password`, `secret`, `token`, `vault`).
- If forbidden keys are present, the agent aborts execution with `AgentStatus.FAILED` and a security violation notice.
- If `allowed_context_keys` is non-empty, only the allowed keys are forwarded to capability workers.

---

## 4. Manifest Specification

Every agent is defined by an `AgentManifest`:
- `id`: Unique lowercase identifier (e.g., `job_discovery_agent`).
- `name`: Display name.
- `category`: `AgentCategory` enum (Recruitment, Computer, Coding, Research, Productivity, Creative, Communication, Automation, Core Orchestration).
- `availability`: `operational`, `limited`, `planned`.
- `capabilities`: List of capability string IDs.
- `model_profile`: Inference configuration (temperature, max tokens, preferred models).
- `context_policy`: Data access restrictions.
- `execution_limits`: Timeout in seconds and maximum retries.

---

## 5. Integration with Multi-Agent Orchestration

During multi-agent DAG execution:
1. The **Supervisor** translates user goals into structured plans via the **Planner**.
2. The **Planner** generates DAG nodes referencing specific `agent_id` targets.
3. The **Scheduler** checks `AgentRegistry.get_manifest(agent_id)`:
   - Verifies the agent is enabled and available.
   - Dispatches execution to the registered `SpecialistAgent`.
4. Outputs are passed to the **Verifier Agent** for schema and contract validation.
5. If verification fails, the **Recovery Agent** determines whether to retry, replan, or pause for user review.

---

## 6. Hardware Safety & Resource Limits

| Resource | Constraint | Enforcement Mechanism |
|---|---|---|
| **GPU VRAM** | 6GB (NVIDIA RTX 4050) | Single-active-model semaphore in `AIGateway` (`Semaphore(1)`). Models are never loaded concurrently. |
| **System RAM** | 16GB Budget | Max output tokens capped at 4,096; context windows limited to 32,768 tokens. |
| **Worker Threads** | CPU Tasks | Non-LLM analysis bounded by `Semaphore(4)` in asynchronous scheduler. |
| **Timeout Guard** | Per-agent limit | Configured in `AgentExecutionLimits.max_execution_time_seconds` (default: 60s - 300s). |

---

## 7. Audit & Diagnostics

The framework provides live diagnostics for every registered agent via `AgentRegistry.run_diagnostic(agent_id)`:
1. **Manifest Validation**: Verifies capability bindings, model profile validity, and context policy safety.
2. **Capability Integrity**: Confirms all declared capabilities exist in `CapabilityRegistry`.
3. **Execution Readiness**: Checks gateway connectivity and availability state.
