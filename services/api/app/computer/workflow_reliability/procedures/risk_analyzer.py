"""Static procedure risk analysis and classification."""

from typing import Any, Dict, List
from app.computer.workflow_reliability.contracts import ProcedureStep, SideEffectClass


class ProcedureRiskAnalyzer:
    """Evaluates procedure steps for destructive, external, and irreversible operations."""

    DESTRUCTIVE_ACTIONS = {"delete", "truncate", "drop", "remove", "overwrite"}
    EXTERNAL_ACTIONS = {"submit", "send", "post", "upload", "email"}

    @classmethod
    def analyze(cls, steps: List[ProcedureStep]) -> Dict[str, Any]:
        """Perform static analysis on procedure steps."""
        destructive_ops: List[str] = []
        external_transmissions: List[str] = []
        irreversible_steps: List[str] = []

        for s in steps:
            act_lower = s.action_type.lower()
            desc_lower = s.description.lower()

            # 1. Destructive check
            if any(d in act_lower or d in desc_lower for d in cls.DESTRUCTIVE_ACTIONS):
                destructive_ops.append(f"{s.step_id} ({s.action_type})")

            # 2. External transmission check
            if any(e in act_lower or e in desc_lower for e in cls.EXTERNAL_ACTIONS):
                external_transmissions.append(f"{s.step_id} ({s.action_type})")

            # 3. Irreversible classification
            if s.side_effect_class in (SideEffectClass.IRREVERSIBLE, SideEffectClass.NON_IDEMPOTENT):
                irreversible_steps.append(f"{s.step_id} ({s.action_type})")

        # Compute overall risk level
        if destructive_ops or len(irreversible_steps) > 2:
            risk_level = "CRITICAL" if destructive_ops else "HIGH"
        elif external_transmissions or irreversible_steps:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        return {
            "risk_level": risk_level,
            "destructive_ops": destructive_ops,
            "external_transmissions": external_transmissions,
            "irreversible_steps": irreversible_steps,
            "total_steps": len(steps),
        }
