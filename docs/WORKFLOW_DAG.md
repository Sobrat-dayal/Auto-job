# Workflow DAG Engine & Dependency Management (Stage 12)

## 1. Directed Acyclic Graph (DAG) Structure

AUTONOM models multi-agent workflows as Directed Acyclic Graphs (`app.orchestration.graph.DependencyGraph`). Each node represents a discrete, verifiable step with explicit dependencies:

```python
class WorkflowStepDefinition(BaseModel):
    step_id: str
    title: str
    capability_id: str
    dependencies: list[str] = []
    input_bindings: dict[str, Any] = {}
    verification_policy: VerificationPolicy
```

---

## 2. Topological Sorting & Kahn's Algorithm

The graph engine constructs in-degree tables and adjacency lists. It computes topological execution order using Kahn's algorithm:

1. Identify all nodes with zero in-degree (`dependencies == []`).
2. Enqueue root nodes.
3. For each dequeued node, decrement in-degrees of successors.
4. If in-degree reaches zero, enqueue successor.
5. If the count of processed nodes does not equal the total number of steps, **a cyclic dependency exists**. The engine fails fast with an explicit error detailing the offending cycle nodes.

---

## 3. Parallel Stage Computation

Steps with identical dependency depths are grouped into execution stages:
- **Stage 0**: Root nodes with no predecessors (e.g. `step_extract`, `step_summarize`, `step_classify`).
- **Stage 1**: Intermediate nodes depending only on Stage 0 outputs (e.g. `step_report`).
- **Stage 2**: Verification / final leaf nodes (e.g. `step_validate`).

Nodes within the same stage can be executed concurrently via `asyncio.gather`, subject to hardware semaphores.

---

## 4. Input Binding Resolution Engine

`WorkflowContext` dynamically resolves mustache-syntax expressions (`{{...}}`) before each step executes:
- `{{input.job_description}}`: Resolves from workflow initial inputs.
- `{{step_extract.extracted_data.technical_skills}}`: Resolves typed lists or dictionaries directly from upstream outputs without forced string coercion.
- `Role: {{step_extract.extracted_data.job_title}}`: Performs embedded string interpolation for template strings.
