# Task Routing & Capability Matching (Stage 12)

## 1. Overview

The **Task Router Agent** (`router`) dispatches workflow steps to qualified agents and capability handlers. Rather than hardcoding agent assignments, routing dynamically evaluates:
- Capability requirements (`capability_id`).
- Agent availability (`is_available`, `enabled`).
- Agent concurrency capacity (`active_assignments < concurrency_limit`).
- Permissions and authorization gates (`requires_authorization`).
- Estimated execution durations.

---

## 2. Explainable Routing Protocol

Every routing decision emits a strongly typed `StepRoutingDecision`:
- `step_id`: Unique step node.
- `capability_id`: Requested capability.
- `assigned_agent_id`: Selected agent.
- `is_fallback`: True if primary candidate was busy or unavailable.
- `explanation`: Human-readable natural language justification for the assignment.
- `candidates_considered`: List of all registered agents offering the capability.

---

## 3. Fallback Hierarchy

```mermaid
flowchart TD
    A[Step Dispatch Request] --> B{Candidates in Registry?}
    B -- No --> F[Fail Fast: Missing Capability]
    B -- Yes --> C{Candidate Available & Under Concurrency?}
    C -- Yes --> D[Assign to Primary Candidate Agent]
    C -- No --> E{Safe Capability Worker Available?}
    E -- Yes --> G[Assign to Capability Worker (Fallback)]
    E -- No --> H[Queue Step for Concurrency Slot]
```

When an assignment begins and finishes, `record_start(agent_id)` and `record_finish(agent_id)` maintain real-time concurrency metrics.
