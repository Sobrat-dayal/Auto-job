"""Precondition and postcondition evaluation for procedure steps."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from app.computer.workflow_reliability.errors import PostconditionFailedError, PreconditionFailedError

logger = logging.getLogger("autonom.reliability.conditions")


class StepConditionEvaluator:
    """Evaluates declarative preconditions prior to action execution and postconditions after."""

    @staticmethod
    def evaluate_preconditions(
        preconditions: List[Dict[str, Any]],
        observed_state: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Check all step preconditions against current observation state."""
        for cond in preconditions:
            c_type = cond.get("type")

            if c_type == "window_title_match":
                expected = cond.get("expected", "").lower()
                current = str(observed_state.get("window_title", "")).lower()
                if expected not in current:
                    return False, f"Window title mismatch: expected '{expected}', found '{current}'."

            elif c_type == "url_origin_match":
                expected_origin = cond.get("expected_origin", "").lower()
                current_url = str(observed_state.get("url", "")).lower()
                if not current_url.startswith(expected_origin):
                    return False, f"URL origin mismatch: expected '{expected_origin}', found '{current_url}'."

            elif c_type == "file_exists":
                # Simulated or verified file existence
                path = cond.get("path")
                if path and not observed_state.get("files_verified", {}).get(path, True):
                    return False, f"Required file does not exist: {path}"

        return True, "Preconditions satisfied"

    @staticmethod
    def evaluate_postconditions(
        postconditions: List[Dict[str, Any]],
        action_result: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Verify post-action state mutations and execution outcomes."""
        for cond in postconditions:
            c_type = cond.get("type")

            if c_type == "mutation_verified":
                expected_status = cond.get("verification_status", "success")
                actual_status = action_result.get("verification_status", "success")
                if expected_status == "success" and actual_status == "failed":
                    return False, "Post-action mutation verification failed."

            elif c_type == "attribute_equals":
                attr = cond.get("attribute")
                expected_val = cond.get("expected")
                actual_val = action_result.get("attributes", {}).get(attr)
                if expected_val != actual_val:
                    return False, f"Attribute '{attr}' mismatch: expected '{expected_val}', found '{actual_val}'."

        return True, "Postconditions verified"
