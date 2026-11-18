# Stage 19: Multi-Agent Coordination & Hybrid Capabilities

## 1. Upgraded Windows Computer Agent (`windows_computer_agent`)

In Stage 19, `windows_computer_agent` (v1.1.0) is upgraded to serve as the primary desktop interaction coordinator. It is registered in `app/orchestration/agents/manifests.py` with expanded scope and 9 new hybrid capabilities:

```json
{
  "agent_id": "windows_computer_agent",
  "name": "Windows Computer Control Agent",
  "version": "1.1.0",
  "role": "Orchestrates multi-method computer automation across Chromium web pages, native Windows UIA applications, legacy Win32 windows, and visual coordinate grounding with context-aware fallback.",
  "capabilities": [
    "desktop_launch_app",
    "desktop_list_windows",
    "desktop_find_element",
    "desktop_invoke_element",
    "desktop_set_value",
    "hybrid_resolve_target",
    "hybrid_probe_methods",
    "hybrid_route_action",
    "hybrid_observe",
    "hybrid_execute",
    "hybrid_click",
    "hybrid_type",
    "hybrid_fallback",
    "hybrid_execute_task"
  ]
}
```

---

## 2. Nine Hybrid Registered Capabilities

Registered in `app/orchestration/capabilities/registry.py` and `app/orchestration/capabilities/computer.py`:

1. **`hybrid_resolve_target`**: Resolves target hints, window titles, DOM selectors, or coordinates into an `InteractionTarget`.
2. **`hybrid_probe_methods`**: Probes all registered interaction adapters for target applicability and confidence.
3. **`hybrid_route_action`**: Runs the scoring model and returns an explainable `RoutingDecisionRecord`.
4. **`hybrid_observe`**: Captures normalized structural and visual observations for a target.
5. **`hybrid_execute`**: Dispatches an action with automatic method routing and verification.
6. **`hybrid_click`**: High-level convenience capability for clicking an element on any surface.
7. **`hybrid_type`**: High-level convenience capability for typing or filling text on any surface.
8. **`hybrid_fallback`**: Triggers a manual or policy-guided fallback to a secondary method.
9. **`hybrid_execute_task`**: Executes an autonomous multi-step instruction with state machine tracking.

---

## 3. Collaboration with Browser and Desktop Specialists

When `SupervisorAgent` delegates a complex workflow (e.g. "Apply for Software Engineer job on Workday"):
1. `browser_agent` manages high-level job portal navigation.
2. If an OS file upload dialog opens (Windows `Open` dialog), `windows_computer_agent` takes control using `WINDOWS_UIA` to select the resume file.
3. If an un-instrumented CAPTCHA or custom canvas element appears, `windows_computer_agent` falls back to `VISUAL_GROUNDING` with user approval.
4. Once completed, control seamlessly returns to the supervisor.
