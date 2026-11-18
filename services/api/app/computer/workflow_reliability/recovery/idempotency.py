"""Idempotency classification and duplicate replay safeguards."""

from typing import Any, Dict
from app.computer.workflow_reliability.contracts import SideEffectClass


class IdempotencyClassifier:
    """Evaluates whether an action is idempotent, repeatable, or requires exactly-once guards."""

    IDEMPOTENT_ACTIONS = {"navigate", "inspect", "select_tab", "focus_window"}
    NON_IDEMPOTENT_ACTIONS = {"submit", "email", "payment", "delete", "post"}

    @classmethod
    def classify_action(
        cls,
        first_arg: str,
        second_arg: Any = None,
        parameters: Any = None,
    ) -> SideEffectClass:
        """Classify action into its appropriate SideEffectClass."""
        # Support both classify_action("browser", "inspect_dom") and classify_action("inspect_dom", {})
        action_type = first_arg
        if isinstance(second_arg, str):
            action_type = second_arg

        act_lower = action_type.lower()

        if any(ro in act_lower for ro in ("inspect", "read", "observe", "get", "capture")):
            return SideEffectClass.READ_ONLY

        if act_lower in cls.IDEMPOTENT_ACTIONS or "navigate" in act_lower:
            return SideEffectClass.IDEMPOTENT

        if any(non_id in act_lower for non_id in ("submit", "send_keys", "email", "payment", "delete", "post")):
            return SideEffectClass.NON_IDEMPOTENT

        return SideEffectClass.IDEMPOTENT
