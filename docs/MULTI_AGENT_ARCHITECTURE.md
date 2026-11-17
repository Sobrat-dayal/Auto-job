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

AUTONOM maintains a strongly typed registry of all agents (`app.orchestration.agents.registry`):

| Agent Identifier | Role | Concurrency | Capabilities | Status (Stage 12) |
|---|---|---|---|---|
| `supervisor` | Workflow Coordinator | 4 | Lifecycle, Checkpoints, Controls | **Active (Stage 12)** |
| `planner` | Dynamic Planner | 2 | Goal Decomposition, DAG, Cycle Check | **Active (Stage 12)** |
| `router` | Capability Dispatcher | 4 | Matching, Concurrency, Fallback | **Active (Stage 12)** |
| `verifier` | Quality Auditor | 2 | Schema Assertions, Semantic Review | **Active (Stage 12)** |
| `recovery` | Fault Diagnostician | 2 | 13-Class Diagnostics, Bounded Retries | **Active (Stage 12)** |
| `capability_worker` | Safe Capability Executor | 4 | 7 Initial Safe Capabilities | **Active (Stage 12)** |
| `job_search_specialist` | Job Discovery Scout | 1 | ATS Feeds, Scoring | *Planned (Stage 14)* |
| `resume_specialist` | Resume Customizer | 1 | Tailoring, ATS Optimization | *Planned (Stage 15)* |
| `browser_specialist` | Web Automation Driver | 1 | Form Filling, Navigation | *Planned (Stage 16)* |

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
