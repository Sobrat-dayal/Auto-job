# Planning Engine & Goal Decomposition (Stage 12)

## 1. Overview

The **Planning Agent** (`planner`) translates high-level user directives into structured, validated execution graphs. It bridges human intent ("Analyze this job description and produce a report") with executable capabilities (`structured_extract`, `text_summarize`, `text_classify`, `data_transform`, `output_validate`).

---

## 2. Planning Protocol

When `PlanningAgent.create_plan()` is called:

1. **AI Gateway Integration**:
   - Queries `AIGateway` with `TaskCategory.PLANNING`.
   - Passes the natural language goal, constraints, and the registered capability catalog.
   - Requests structured JSON containing a list of `WorkflowStepDefinition` objects.
2. **Deterministic Fallback Templates**:
   - If no LLM provider is configured or an API error occurs, the Planning Agent automatically activates specialized deterministic plan templates:
     - **Job & Recruitment Analysis Workflow**: Extracts technical skills, summarizes responsibilities, classifies domain, compiles markdown report, and validates output.
     - **Code Inspection Workflow**: AST syntax check and complexity validation.
     - **Text Analysis Workflow**: Summarize, transform, and validate.
3. **DAG Verification & Fast Cycle Detection**:
   - Constructs `DependencyGraph(steps)`.
   - Runs Kahn's algorithm to ensure the graph is strictly acyclic.
   - If a cyclic dependency is detected from an AI output, sanitizes dependencies into a safe sequential chain.
4. **Plan Versioning**:
   - Every generated plan receives a monotonic version (`v1` for initial, `v2+` on replans). Prior versions are preserved in SQLite for audit history.
