"""Parameter binding, validation, and type resolution for reusable procedures."""

from typing import Any, Dict, List, Tuple
from app.computer.workflow_reliability.contracts import ProcedureParameter
from app.computer.workflow_reliability.errors import ProcedureValidationError


class ParameterEngine:
    """Validates and binds runtime arguments to procedure parameter contracts."""

    @staticmethod
    def validate_and_bind(
        parameters: List[ProcedureParameter],
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate input arguments against parameter definitions and supply defaults."""
        bound: Dict[str, Any] = {}
        missing: List[str] = []

        param_map = {p.name: p for p in parameters}

        # 1. Check all required parameters
        for p in parameters:
            if p.name in arguments and arguments[p.name] is not None:
                val = arguments[p.name]
                bound[p.name] = ParameterEngine._cast_type(p.name, p.type, val)
            elif p.default_value is not None:
                bound[p.name] = p.default_value
            elif p.required:
                missing.append(p.name)

        if missing:
            raise ProcedureValidationError(f"Missing required procedure parameters: {', '.join(missing)}")

        # 2. Include any additional optional arguments
        for k, v in arguments.items():
            if k not in bound:
                bound[k] = v

        return bound

    @staticmethod
    def _cast_type(name: str, expected_type: str, val: Any) -> Any:
        try:
            if expected_type == "number":
                return float(val) if "." in str(val) else int(val)
            if expected_type == "boolean":
                if isinstance(val, bool):
                    return val
                return str(val).lower() in ("true", "1", "yes")
            if expected_type == "string" or expected_type == "filepath" or expected_type == "url":
                return str(val)
            return val
        except Exception as exc:
            raise ProcedureValidationError(f"Parameter '{name}' could not be cast to '{expected_type}': {exc}")
