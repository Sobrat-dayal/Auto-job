"""Procedure schema and structural validation."""

from typing import List
from app.computer.workflow_reliability.contracts import ReusableProcedure
from app.computer.workflow_reliability.errors import ProcedureValidationError


class ProcedureValidator:
    """Enforces integrity, uniqueness, and structural rules on ReusableProcedure instances."""

    @classmethod
    def validate(cls, procedure: ReusableProcedure, raise_exception: bool = False) -> List[str]:
        """Validate procedure definition; returns list of issues, optionally raising ProcedureValidationError."""
        issues: List[str] = []
        if not procedure.name or not procedure.name.strip():
            issues.append("Procedure name cannot be empty.")

        if procedure.version < 1:
            issues.append(f"Invalid procedure version: {procedure.version}")

        # 1. Step uniqueness
        step_ids = set()
        for idx, s in enumerate(procedure.steps):
            if not s.step_id:
                issues.append(f"Step at index {idx} has missing step_id.")
            elif s.step_id in step_ids:
                issues.append(f"Duplicate step_id detected: '{s.step_id}'.")
            step_ids.add(s.step_id)

            if getattr(s, "timeout_seconds", 30) <= 0:
                issues.append(f"Step '{s.step_id}' must have positive timeout_seconds.")

        # 2. Parameter name uniqueness
        param_names = set()
        for p in procedure.parameters:
            if not p.name or not p.name.strip():
                issues.append("Procedure parameter name cannot be empty.")
            elif p.name in param_names:
                issues.append(f"Duplicate parameter name detected: '{p.name}'.")
            param_names.add(p.name)

        # 3. Check for unsupported arbitrary code flags
        if hasattr(procedure, "custom_script") or any("script" in s.input_bindings for s in procedure.steps):
            issues.append("Arbitrary executable scripts are prohibited in declarative procedures.")

        if raise_exception and issues:
            raise ProcedureValidationError("; ".join(issues))
        return issues
