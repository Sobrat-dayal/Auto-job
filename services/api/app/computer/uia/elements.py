"""Extraction and mapping of IUIAutomationElement attributes and patterns (Stage 17)."""

import logging
from typing import Any

from app.computer.contracts import UIElementInfo, WindowBounds

logger = logging.getLogger("autonom.computer.uia.elements")

# Mapping of UIAutomation ControlType IDs to readable strings
CONTROL_TYPE_NAMES: dict[int, str] = {
    50000: "Button",
    50001: "Calendar",
    50002: "CheckBox",
    50003: "ComboBox",
    50004: "Edit",
    50005: "Hyperlink",
    50006: "Image",
    50007: "ListItem",
    50008: "List",
    50009: "Menu",
    50010: "MenuBar",
    50011: "MenuItem",
    50012: "ProgressBar",
    50013: "RadioButton",
    50014: "ScrollBar",
    50015: "Slider",
    50016: "Spinner",
    50017: "StatusBar",
    50018: "Tab",
    50019: "TabItem",
    50020: "Text",
    50021: "ToolBar",
    50022: "ToolTip",
    50023: "Tree",
    50024: "TreeItem",
    50025: "Custom",
    50026: "Group",
    50028: "DataGrid",
    50029: "DataItem",
    50030: "Document",
    50031: "SplitButton",
    50032: "Window",
    50033: "Pane",
    50036: "Table",
    50037: "TitleBar",
    50038: "Separator",
}

# Supported control pattern IDs in UIAutomation
PATTERN_IDS: dict[str, int] = {
    "invoke": 10000,
    "selection": 10001,
    "value": 10002,
    "scroll": 10004,
    "expand_collapse": 10005,
    "toggle": 10015,
    "selection_item": 10010,
    "table": 10012,
    "text": 10014,
}


class UIElementExtractor:
    """Extracts typed properties and supported control patterns from an IUIAutomationElement."""

    @staticmethod
    def extract_element_info(element: Any, window_ref: str, index_path: str = "0") -> UIElementInfo:
        """Converts an IUIAutomationElement COM object into a serializable UIElementInfo."""
        try:
            name = element.CurrentName
        except Exception:
            name = None

        try:
            auto_id = element.CurrentAutomationId
        except Exception:
            auto_id = None

        try:
            type_id = int(element.CurrentControlType)
            type_name = CONTROL_TYPE_NAMES.get(type_id, f"Custom({type_id})")
        except Exception:
            type_id = 0
            type_name = "Unknown"

        try:
            class_name = element.CurrentClassName
        except Exception:
            class_name = None

        try:
            framework_id = element.CurrentFrameworkId
        except Exception:
            framework_id = None

        try:
            is_enabled = bool(element.CurrentIsEnabled)
        except Exception:
            is_enabled = True

        try:
            is_offscreen = bool(element.CurrentIsOffscreen)
        except Exception:
            is_offscreen = False

        try:
            has_focus = bool(element.CurrentHasKeyboardFocus)
        except Exception:
            has_focus = False

        # Bounding rectangle
        try:
            rect = element.CurrentBoundingRectangle
            bounds = WindowBounds(
                left=int(rect.left),
                top=int(rect.top),
                right=int(rect.right),
                bottom=int(rect.bottom),
                width=max(0, int(rect.right - rect.left)),
                height=max(0, int(rect.bottom - rect.top)),
            )
        except Exception:
            bounds = WindowBounds(left=0, top=0, right=0, bottom=0, width=0, height=0)

        # Detect supported patterns
        supported_patterns: list[str] = []
        value = None
        toggle_state = None

        for pattern_name, pattern_id in PATTERN_IDS.items():
            try:
                pattern_obj = element.GetCurrentPattern(pattern_id)
                if pattern_obj:
                    supported_patterns.append(pattern_name)

                    if pattern_name == "value":
                        try:
                            from comtypes.gen.UIAutomationClient import IUIAutomationValuePattern
                            val_pat = pattern_obj.QueryInterface(IUIAutomationValuePattern)
                            value = val_pat.CurrentValue
                        except Exception:
                            pass
                    elif pattern_name == "toggle":
                        try:
                            from comtypes.gen.UIAutomationClient import IUIAutomationTogglePattern
                            tog_pat = pattern_obj.QueryInterface(IUIAutomationTogglePattern)
                            state = int(tog_pat.CurrentToggleState)
                            # 0: Off, 1: On, 2: Indeterminate
                            toggle_state = "on" if state == 1 else "off" if state == 0 else "indeterminate"
                        except Exception:
                            pass
            except Exception:
                continue

        element_ref = f"el_{window_ref}_{index_path}_{auto_id or type_name.lower()}"

        return UIElementInfo(
            element_ref=element_ref,
            window_ref=window_ref,
            name=name,
            automation_id=auto_id,
            control_type=type_name,
            control_type_id=type_id,
            class_name=class_name,
            framework_id=framework_id,
            is_enabled=is_enabled,
            is_offscreen=is_offscreen,
            has_keyboard_focus=has_focus,
            bounding_box=bounds,
            supported_patterns=supported_patterns,
            value=value,
            toggle_state=toggle_state,
        )


element_extractor = UIElementExtractor()
