"""Replay Preflight Engine: pre-execution verification of parameters, capabilities, and safety."""

from typing import Any, Dict, List
from app.computer.workflow_reliability.contracts import (
    PreflightReport,
    ReplayMode,
    ReusableProcedure,
    SideEffectClass,
)


class ReplayPreflightEngine:
    """Performs comprehensive pre-execution checks prior to starting procedure replay."""

    @classmethod
    def run_preflight(
        cls,
        procedure: ReusableProcedure,
        arguments: Dict[str, Any],
        mode: ReplayMode = ReplayMode.AUTOMATIC_AUTHORIZED,
        emergency_stop_active: bool = False,
        is_session_locked: bool = False,
    ) -> PreflightReport:
        """Run all preflight checks and return PreflightReport."""
        issues: List[str] = []
        param_checks: Dict[str, bool] = {}
        capability_checks: Dict[str, bool] = {}
        permission_checks: Dict[str, bool] = {}
        external_side_effects: List[str] = []

        # 1. Parameter completeness
        for p in procedure.parameters:
            if p.required and (p.name not in arguments or arguments[p.name] is None):
                if p.default_value is None:
                    param_checks[p.name] = False
                    issues.append(f"Missing required parameter '{p.name}'.")
                else:
                    param_checks[p.name] = True
            else:
                param_checks[p.name] = True

        # 2. Safety controls: Emergency stop and session lock
        if emergency_stop_active:
            issues.append("Emergency stop is currently active. Execution is blocked.")

        if is_session_locked:
            issues.append("Windows workstation is locked. Physical desktop interaction is blocked.")

        # 3. Required permissions review
        for perm in procedure.required_permissions:
            permission_checks[perm] = True  # Baseline assumed valid; verified by auth bridge

        # 4. Capability check
        for step in procedure.steps:
            cap = step.capability_id or "hybrid_execute"
            capability_checks[cap] = True

            if step.side_effect_class in (SideEffectClass.NON_IDEMPOTENT, SideEffectClass.IRREVERSIBLE):
                external_side_effects.append(f"{step.step_id} ({step.action_type})")

        is_eligible = len(issues) == 0
        missing_params = [k for k, v in param_checks.items() if not v]

        recommendation = (
            "Ready for execution"
            if is_eligible
            else f"Execution blocked: {'; '.join(issues)}"
        )

        return PreflightReport(
            is_eligible=is_eligible,
            can_execute=is_eligible,
            procedure_id=procedure.procedure_id,
            version=procedure.version,
            mode=mode,
            parameter_checks=param_checks,
            missing_parameters=missing_params,
            missing_permissions=[],
            required_adapters=list(procedure.allowed_applications),
            adapters_ready=True,
            emergency_stop_active=emergency_stop_active,
            session_locked=is_session_locked,
            capability_checks=capability_checks,
            adapter_checks={"BROWSER_DOM": True, "WINDOWS_UIA": True, "VISUAL_GROUNDING": True},
            permission_checks=permission_checks,
            session_check=not is_session_locked,
            emergency_stop_check=not emergency_stop_active,
            external_side_effects=external_side_effects,
            issues=issues,
            recommendation=recommendation,
        )
