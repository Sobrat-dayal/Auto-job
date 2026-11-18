# Accessibility Tree Inspection & Serialization Specification (Stage 17)

## 1. Overview

Directly passing raw Win32 visual structures to Large Language Models is inefficient, noisy, and prone to context window exhaustion. Complex applications like Microsoft Word or Visual Studio Code contain tens of thousands of visual nodes (scrollbars, borders, content presenters, virtualizing viewports).

The `UITreeInspector` (`app/computer/uia/trees.py`) implements bounded, semantically filtered tree traversal that extracts essential structural information while strictly constraining token consumption and execution latency.

---

## 2. Tree Traversal Mechanics

### `ControlViewWalker` vs. `RawViewWalker`

- **Control View (Default)**:
  Uses `uia.ControlViewWalker`. It traverses only elements that map directly to functional controls visible to users (buttons, inputs, lists, windows), skipping redundant layout wrappers.
- **Raw View**:
  Uses `uia.RawViewWalker`. Used for low-level debugging or non-standard custom controls that do not register standard control types.

### Bounding Guards

Every inspection request accepts `InspectionOptions`:
- `max_depth`: Default `6` (configurable 1–20). Prevents infinite descent into recursive custom tree nodes.
- `max_nodes`: Default `250` (configurable 5–1000). Stops traversal once node budget is reached and flags `is_truncated = True`.
- `timeout_ms`: Default `10000` ms. Enforced by `UIAWorkerSupervisor`.

---

## 3. Element Extraction Contract: `UIElementInfo`

For every visited node, `UIElementExtractor` captures:
- `element_ref`: Synthetic deterministic path identifier (`el_{depth}_{index}`).
- `window_ref`: Owning window reference.
- `name`: Accessible text label or header.
- `automation_id`: Developer-assigned ID (e.g., `"SaveButton"` or `"txtEmail"`).
- `control_type`: Human-readable type string (`"Button"`, `"Edit"`, `"CheckBox"`).
- `control_type_id`: Numeric UIA type ID (50000–50038).
- `class_name`: Native window or framework class (`"TextBox"`, `"Button"`, `"Chrome_RenderWidgetHostHWND"`).
- `framework_id`: Underlying framework (`"WPF"`, `"Win32"`, `"WinForm"`, `"DirectUI"`, `"XAML"`).
- `is_enabled`: Control interactivity state.
- `bounding_box`: Screen bounds `{ left, top, right, bottom, width, height }`.
- `supported_patterns`: List of supported control pattern names (`["invoke", "value", "toggle"]`).
- `value`: Current text value for edit controls (sanitized via `PrivacyFilter`).
- `toggle_state`: `"on"`, `"off"`, or `"indeterminate"`.

---

## 4. LLM Prompt Compilation: `UISnapshotCompiler`

To feed accessibility structures into the AI Model Gateway (Stage 11), `UISnapshotCompiler` produces an ultra-compact outline format:

```text
=== WINDOW: Downloads - File Explorer (win_200412_5832) ===
Total Nodes: 18 | Truncated: False
--- ACCESSIBILITY TREE ---
[Window] 'Downloads - File Explorer' (id='TitleBar', pat=[window])
  [ToolBar] 'Ribbon Tabs'
    [TabItem] 'Home' (pat=[selection_item])
    [TabItem] 'View' (pat=[selection_item])
  [Pane] 'Address Bar'
    [Edit] 'Address' (val='C:\Users\User\Downloads', pat=[value])
  [Table] 'Items View' (pat=[table,grid])
    [ListItem] 'Resume_2026.pdf' (pat=[selection_item])
    [ListItem] 'Cover_Letter.docx' (pat=[selection_item])
```

This compact outline provides complete situational awareness to the AI agent in under 200 tokens.
