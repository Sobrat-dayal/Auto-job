"""Execution of standard Microsoft UI Automation control patterns (Stage 17)."""

import logging
from typing import Any

from app.computer.uia.elements import PATTERN_IDS

logger = logging.getLogger("autonom.computer.uia.patterns")


class PatternExecutionError(Exception):
    """Raised when a control pattern operation fails or is unsupported."""
    pass


class PatternExecutor:
    """Executes standard UIA control patterns on IUIAutomationElement COM objects."""

    @staticmethod
    def invoke(element: Any) -> bool:
        """Invokes a button, menu item, or command control via InvokePattern."""
        pattern_id = PATTERN_IDS["invoke"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support InvokePattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationInvokePattern
            inv_pat = pattern_obj.QueryInterface(IUIAutomationInvokePattern)
            inv_pat.Invoke()
            return True
        except Exception as e:
            logger.error(f"InvokePattern failed: {e}")
            raise PatternExecutionError(f"InvokePattern execution error: {e}")

    @staticmethod
    def set_value(element: Any, text: str) -> bool:
        """Sets the value of an editable control via ValuePattern."""
        pattern_id = PATTERN_IDS["value"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support ValuePattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationValuePattern
            val_pat = pattern_obj.QueryInterface(IUIAutomationValuePattern)
            val_pat.SetValue(text)
            return True
        except Exception as e:
            logger.error(f"ValuePattern failed: {e}")
            raise PatternExecutionError(f"ValuePattern execution error: {e}")

    @staticmethod
    def get_value(element: Any) -> str:
        """Reads the current text value of a control via ValuePattern or TextPattern."""
        # Try ValuePattern first
        val_id = PATTERN_IDS["value"]
        try:
            pattern_obj = element.GetCurrentPattern(val_id)
            if pattern_obj:
                from comtypes.gen.UIAutomationClient import IUIAutomationValuePattern
                val_pat = pattern_obj.QueryInterface(IUIAutomationValuePattern)
                return str(val_pat.CurrentValue or "")
        except Exception:
            pass

        # Fallback to TextPattern
        text_id = PATTERN_IDS["text"]
        try:
            pattern_obj = element.GetCurrentPattern(text_id)
            if pattern_obj:
                from comtypes.gen.UIAutomationClient import IUIAutomationTextPattern
                text_pat = pattern_obj.QueryInterface(IUIAutomationTextPattern)
                doc_range = text_pat.DocumentRange
                return str(doc_range.GetText(-1) or "")
        except Exception:
            pass

        # Final fallback to element CurrentName
        try:
            return str(element.CurrentName or "")
        except Exception:
            return ""

    @staticmethod
    def toggle(element: Any) -> str:
        """Toggles a checkbox or switch control via TogglePattern. Returns new state ('on'|'off')."""
        pattern_id = PATTERN_IDS["toggle"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support TogglePattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationTogglePattern
            tog_pat = pattern_obj.QueryInterface(IUIAutomationTogglePattern)
            tog_pat.Toggle()
            state = int(tog_pat.CurrentToggleState)
            return "on" if state == 1 else "off" if state == 0 else "indeterminate"
        except Exception as e:
            logger.error(f"TogglePattern failed: {e}")
            raise PatternExecutionError(f"TogglePattern execution error: {e}")

    @staticmethod
    def select(element: Any) -> bool:
        """Selects an item via SelectionItemPattern."""
        pattern_id = PATTERN_IDS["selection_item"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support SelectionItemPattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationSelectionItemPattern
            sel_pat = pattern_obj.QueryInterface(IUIAutomationSelectionItemPattern)
            sel_pat.Select()
            return True
        except Exception as e:
            logger.error(f"SelectionItemPattern failed: {e}")
            raise PatternExecutionError(f"SelectionItemPattern execution error: {e}")

    @staticmethod
    def expand(element: Any) -> bool:
        """Expands a combo box, tree node, or menu via ExpandCollapsePattern."""
        pattern_id = PATTERN_IDS["expand_collapse"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support ExpandCollapsePattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationExpandCollapsePattern
            exp_pat = pattern_obj.QueryInterface(IUIAutomationExpandCollapsePattern)
            exp_pat.Expand()
            return True
        except Exception as e:
            logger.error(f"ExpandCollapsePattern (Expand) failed: {e}")
            raise PatternExecutionError(f"ExpandCollapsePattern execution error: {e}")

    @staticmethod
    def collapse(element: Any) -> bool:
        """Collapses an expanded control via ExpandCollapsePattern."""
        pattern_id = PATTERN_IDS["expand_collapse"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support ExpandCollapsePattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationExpandCollapsePattern
            exp_pat = pattern_obj.QueryInterface(IUIAutomationExpandCollapsePattern)
            exp_pat.Collapse()
            return True
        except Exception as e:
            logger.error(f"ExpandCollapsePattern (Collapse) failed: {e}")
            raise PatternExecutionError(f"ExpandCollapsePattern execution error: {e}")

    @staticmethod
    def scroll(element: Any, horizontal_percent: float = -1.0, vertical_percent: float = -1.0) -> bool:
        """Scrolls container via ScrollPattern."""
        pattern_id = PATTERN_IDS["scroll"]
        try:
            pattern_obj = element.GetCurrentPattern(pattern_id)
            if not pattern_obj:
                raise PatternExecutionError("Element does not support ScrollPattern")

            from comtypes.gen.UIAutomationClient import IUIAutomationScrollPattern
            scroll_pat = pattern_obj.QueryInterface(IUIAutomationScrollPattern)
            # ScrollAmount: 0 = LargeDecrement, 1 = SmallDecrement, 2 = NoAmount, 3 = LargeIncrement, 4 = SmallIncrement
            h_amount = 3 if horizontal_percent > 0 else 1 if horizontal_percent < 0 else 2
            v_amount = 3 if vertical_percent > 0 else 1 if vertical_percent < 0 else 2
            scroll_pat.Scroll(h_amount, v_amount)
            return True
        except Exception as e:
            logger.error(f"ScrollPattern failed: {e}")
            raise PatternExecutionError(f"ScrollPattern execution error: {e}")


pattern_executor = PatternExecutor()
