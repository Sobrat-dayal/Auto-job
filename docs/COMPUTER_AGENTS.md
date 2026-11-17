# AUTONOM — Computer & OS Operation Agents Architecture

## 1. Overview

AUTONOM includes a dedicated suite of **4 Computer Control & OS Operation Agents** designed to enable autonomous desktop assistance, browser navigation, and application interaction on Windows 11.

In accordance with Stage 13's strict principle of **Honest Availability**, these agents are explicitly marked as `limited`. Their planning, metadata analysis, coordinate calculation, and action-sequencing capabilities are fully operational, while direct unauthorized Windows input injection (mouse/keyboard API hooks) remains guarded until dedicated safety stages.

---

## 2. The 4 Computer Specialists

```
               [User Goal / Task Request]
                           |
                           v
        +-------------------------------------+
        |       Windows Computer Agent        | -> Formulates OS Operation Plan
        +------------------+------------------+
                           |
           +---------------+---------------+
           |                               |
           v                               v
+----------------------+       +-----------------------+
|Visual Grounding Agent|       |  Structural UI Agent  |
|Image Metadata & BBox |       |Windows UIA & DOM Tree |
+----------+-----------+       +-----------+-----------+
           |                               |
           +---------------+---------------+
                           |
                           v
        +-------------------------------------+
        |       Browser Automation Agent      | -> Formulates Web Navigation Plan
        +-------------------------------------+
```

### 2.1 Windows Computer Agent (`windows_computer_agent`)
- **Category**: Computer | **Availability**: Limited
- **Role**: Plans desktop window interactions, application launching, file-explorer operations, and system automation workflows.
- **Key Capabilities**:
  - `desktop_plan_operation`: Translates high-level desktop instructions into structured action sequences (launch, focus, keypress, click, wait).

### 2.2 Browser Automation Agent (`browser_agent`)
- **Category**: Computer | **Availability**: Limited
- **Role**: Plans web browser workflows (navigating to URLs, filling forms, clicking elements, downloading documents).
- **Key Capabilities**:
  - `browser_plan_navigation`: Decomposes browser goals into structured navigation steps (goto, click, type, submit, assert).

### 2.3 Visual Grounding Agent (`visual_grounding_agent`)
- **Category**: Computer | **Availability**: Limited
- **Role**: Inspects visual UI screenshots, identifies target UI elements, and calculates normalized coordinate bounding boxes.
- **Key Capabilities**:
  - `visual_inspect_image_metadata`: Extracts image resolution, color depth, format, and simulated bounding box coordinates for visual elements.

### 2.4 Structural UI Agent (`structural_ui_agent`)
- **Category**: Computer | **Availability**: Limited
- **Role**: Parses Windows UI Automation (UIA) trees and web DOM trees into clean semantic representations for agent reasoning.
- **Key Capabilities**:
  - `structural_parse_accessibility_tree`: Filters noisy UI trees into actionable node hierarchies with roles, names, and automation IDs.

---

## 3. Safety Guardrails & Human-in-the-Loop Policy

1. **Read-Only Inspection**:
   Visual grounding and accessibility tree parsing are completely safe and read-only.
2. **Action Plan Pre-Approval**:
   All plans produced by `desktop_plan_operation` or `browser_plan_navigation` require confirmation or supervisor verification before execution.
3. **No Direct Hardware Injection in Stage 13**:
   Low-level Win32 `SendInput` and raw mouse event dispatching are strictly withheld from Stage 13 execution, preventing accidental desktop hijacking during test cycles.
