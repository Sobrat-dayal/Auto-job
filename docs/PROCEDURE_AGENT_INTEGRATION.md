# Procedure Agent Integration & Multi-Agent Coordination

## 1. Overview & Agent Architecture

Stage 20 integrates workflow recording, compilation, replay, and recovery into AUTONOM's multi-agent architecture. Three primary agents coordinate to manage the lifecycle of automated procedures:

1. **`windows_computer_agent` (v1.2.0)**: Upgraded with Stage 20 capabilities to author, test, and execute procedures autonomously.
2. **`recovery_agent` (v1.1.0)**: Monitors active executions, detects crashes or stalls, inspects checkpoints, and issues recovery continuation requests.
3. **`supervisor_agent`**: Oversees high-level job application objectives, selects reusable procedures from the library, and delegates execution steps.

---

## 2. Capability Registration & Manifest

The Stage 20 capabilities are registered in `app/orchestration/capabilities/registry.py` and exposed in `app/orchestration/agents/manifests.py`:

```python
# windows_computer_agent manifest snippet
AgentManifest(
    agent_id="windows_computer_agent",
    name="Windows Computer Control Agent",
    version="1.2.0",
    description="Operational specialist for hybrid computer interaction, procedure recording, replay, and workflow recovery.",
    capabilities=[
        # Stage 17 UIA Capabilities
        "desktop_discover_windows", "desktop_inspect_tree", "desktop_click_element", ...
        # Stage 18 Visual Capabilities
        "visual_capture_screen", "visual_ocr_search", "visual_click_coordinate", ...
        # Stage 19 Hybrid Capabilities
        "hybrid_resolve_target", "hybrid_route_action", "hybrid_execute", ...
        # Stage 20 Reliability & Procedure Capabilities
        "reliability_start_recording",
        "reliability_stop_recording",
        "reliability_compile_procedure",
        "reliability_execute_procedure",
        "reliability_resume_execution"
    ],
    state=AvailabilityState.OPERATIONAL
)
```

---

## 3. Multi-Agent Workflow Scenario

### Automated Job Application Flow
```
+----------------------------------------------------------------------------------------------------+
| 1. Supervisor receives user goal: "Apply to Senior Python Engineer at TechCorp"                    |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| 2. Supervisor queries Procedure Library for matching procedure ("TechCorp Workday Application")   |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| 3. Supervisor delegates execution to `windows_computer_agent` with parameters:                     |
|    - applicant_name: "Jane Doe"                                                                    |
|    - resume_path: "C:\\Docs\\Jane_Doe_Resume.pdf"                                                  |
|    - email: "jane@example.com"                                                                     |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
| 4. `windows_computer_agent` executes procedure:                                                    |
|    - Navigates to job portal                                                                       |
|    - Fills applicant fields                                                                        |
|    - Uploads resume file                                                                           |
|    - Generates step-by-step checkpoints                                                            |
|    - Reaches non-idempotent "Submit Application" button -> Checks policy & Intent Hash             |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v (Network Timeout Occurs)
+----------------------------------------------------------------------------------------------------+
| 5. `recovery_agent` intervenes:                                                                    |
|    - Reads latest valid checkpoint                                                                 |
|    - Inspects external side-effect ledger                                                          |
|    - Formulates `RecoveryPlan`                                                                     |
|    - Instructs `windows_computer_agent` to resume safely without re-submitting duplicate files    |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Capability Execution Protocol

When an agent executes a reliability capability, the capability dispatches directly to the singleton `WorkflowReliabilityService`:

```python
class ExecuteProcedureCapability(BaseCapability):
    capability_id = "reliability_execute_procedure"
    name = "Execute Reusable Procedure"
    
    async def execute(self, context: ExecutionContext, parameters: dict[str, Any]) -> dict[str, Any]:
        service = WorkflowReliabilityService.get_instance()
        procedure_id = parameters["procedure_id"]
        inputs = parameters.get("inputs", {})
        mode = parameters.get("mode", "automatic_authorized")
        
        execution = await service.execute_procedure(
            procedure_id=procedure_id,
            parameter_values=inputs,
            mode=mode,
            actor_id=context.agent_id
        )
        return {"execution_id": execution.execution_id, "status": execution.status}
```

This ensures unified execution logic, shared security boundaries, and consistent audit telemetry across all human and agent interactions.
