# Visual Agent Integration & Capabilities (Stage 18)

## 1. Specialist Agent: `VisualGroundingAgent`

Stage 18 promotes the `visual_grounding_agent` to **`OPERATIONAL`** status within the AUTONOM multi-agent catalog (`app/orchestration/agents/manifests.py`):

```python
AgentManifest(
    id="visual_grounding_agent",
    name="Visual Grounding Agent",
    role="Visual perception, screen capture, OCR, and coordinate automation specialist",
    category=AgentCategory.COMPUTER,
    availability=AvailabilityState.OPERATIONAL,
    capabilities=[
        "visual_capture_display",
        "visual_capture_window",
        "visual_run_ocr",
        "visual_find_text",
        "visual_detect_elements",
        "visual_ground",
        "visual_execute_action",
        "visual_click",
        "visual_enter_text",
    ],
    ...
)
```

---

## 2. Capability Registry Definitions

The 9 visual capabilities (`app/orchestration/capabilities/computer.py`) are registered into the central capability registry:

| Capability Name | Privileges Required | Description |
|---|---|---|
| `visual_capture_display` | `read:screen` | Captures primary or indexed physical display screenshot |
| `visual_capture_window` | `read:screen` | Isolates and captures active application window via GDI/WGC |
| `visual_run_ocr` | `read:screen` | Runs offline WinRT OCR on latest session frame |
| `visual_find_text` | `read:screen` | Matches text query against OCR result and returns bounding boxes |
| `visual_detect_elements` | `read:screen` | Extracts interactive UI controls and categorized element list |
| `visual_ground` | `read:screen` | Grounds natural language element query into desktop coordinate |
| `visual_execute_action` | `write:input` | Dispatches arbitrary visual action (click, type, drag, scroll) |
| `visual_click` | `write:input` | Quick coordinate or element-targeted mouse click |
| `visual_enter_text` | `write:input` | Types text into grounded or focused control |

---

## 3. Workflow Orchestration with Supervisor

When the Supervisor executes an end-to-end recruitment or document management workflow:
1. It attempts structural UIA automation first if the application supports it (Stage 17).
2. If controls are unmapped, custom-drawn, or virtualized, the Supervisor dynamically routes the task to `VisualGroundingAgent`.
3. `VisualGroundingAgent` captures the active window, grounds the target control via OCR/VLM, clicks the element, and verifies the state transition.
4. Returns execution results and visual difference metrics to the Supervisor for next-step planning.
