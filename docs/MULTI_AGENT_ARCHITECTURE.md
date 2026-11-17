# AUTONOM Multi-Agent Architecture (Stage 12)

## 1. Executive Summary

Stage 12 establishes the production-grade **Multi-Agent Orchestration Runtime** for AUTONOM. While Stage 11 provided unified AI model inference and routing, Stage 12 coordinates autonomous intelligent agents to plan, decompose, schedule, execute, verify, and recover complex workflows.

The system is built upon **5 Core Logical Agents**:
1. **Supervisor Agent (`supervisor`)**: Master coordinator orchestrating workflow lifecycles, user governance, checkpoints, and graceful recovery.
2. **Planning Agent (`planner`)**: Decomposes natural language directives into structured, validated Directed Acyclic Graphs (DAGs) with strict cycle detection and versioning.
3. **Task Router Agent (`router`)**: Matches step requirements to capable agents and execution handlers, enforcing concurrency limits, hardware constraints, and permissions with full explainability.
4. **Verification Agent (`verifier`)**: Multi-layer audit agent executing deterministic schema/type assertions and semantic model evaluations.
5. **Recovery Agent (`recovery`)**: Fault diagnostician classifying failures across 13 normalized categories and executing bounded retries or dynamic replanning.

In addition, the **Safe Capability Worker (`capability_worker`)** executes registered deterministic and AI-assisted capabilities out-of-the-box.

---

## 2. Agent Registry & Specialist Roles

In Stage 12, the initial 5 core orchestration agents and `capability_worker` were introduced. In **Stage 13**, the architecture expanded into the **Specialist AI Agent Framework** with a manifest-driven catalog containing all 24 agents across 9 functional categories.

Refer to the complete Stage 13 specifications:
- [Specialist AI Agent Framework](file:///e:/proooo/AUTO%20JOB/docs/SPECIALIST_AGENT_FRAMEWORK.md)
- [Specialist AI Agent Catalog (All 24 Agents)](file:///e:/proooo/AUTO%20JOB/docs/SPECIALIST_AGENT_CATALOG.md)
- [Agent Manifest Specification](file:///e:/proooo/AUTO%20JOB/docs/AGENT_MANIFESTS.md)
- [Agent Model Profiles](file:///e:/proooo/AUTO%20JOB/docs/AGENT_MODEL_PROFILES.md)

| Category | Agent Count | Availability Summary | Key Capabilities |
|---|---|---|---|
| **Core Orchestration** | 5 | Operational | Dynamic planning, DAG scheduling, routing, verification, recovery |
| **Capability Worker** | 1 | Operational | General execution worker |
| **Recruitment** | 6 | Operational / Limited | Job discovery, skill matching, resume tailoring, ATS field classification, recruiter comms, interview prep |
| **Computer Operations**| 4 | Limited | Visual grounding, structural UIA/DOM trees, browser planning, desktop planning |
| **Coding** | 1 | Operational | Code explanation, static code review, automated test generation |
| **Research** | 2 | Operational | Multi-source synthesis, evidence extraction, market salary analysis |
| **Productivity** | 3 | Operational | Document drafting, spreadsheet analysis & formula explanation, slide deck creation |
| **Creative & Comms** | 2 | Operational / Limited | Scene specifications, message classification, draft responses |
| **Automation** | 1 | Operational | Template generation, DAG validation |

---

## 3. Concurrency & Hardware Guardrails (NVIDIA RTX 4050 6GB)

AUTONOM strictly adheres to physical hardware boundaries:
- **Local LLM Execution Guardrail**: An asynchronous semaphore (`asyncio.Semaphore(1)`) guarantees that at most **one active model** executes inference in GPU VRAM at any moment.
- **Parallel Non-LLM Execution**: Pure Python deterministic capabilities (AST inspection, regex extraction, schema validation, markdown formatting) run concurrently up to 4 parallel workers (`asyncio.Semaphore(4)`).
- **Graceful Queueing**: When multiple steps in a DAG stage require local AI generation, they queue transparently without causing GPU Out-Of-Memory (OOM) faults.

---

## 4. Execution Lifecycle

```
[ User Natural Language Goal ]
              │
              ▼
    [ Supervisor Agent ]
              │
              ▼
     [ Planning Agent ] ───► [ Validated DAG Plan (v1) ]
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
      [ Independent Step 1 ]                         [ Independent Step 2 ]
              │                                               │
    [ Task Router Agent ]                           [ Task Router Agent ]
              │                                               │
    [ Capability Execution ]                        [ Capability Execution ]
              │                                               │
    [ Verification Agent ]                          [ Verification Agent ]
              │                                               │
              └───────────────────────┬───────────────────────┘
                                      ▼
                             [ Dependent Step 3 ]
                                      │
                             [ Verification Agent ]
                                      │
                                      ▼
                        [ Final Workflow Artifact ]
```
