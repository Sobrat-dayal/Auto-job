"""Output validation capability for deterministic schema and contract assertions."""

from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy


class OutputValidateCapability(BaseCapability):
    """Validates arbitrary output dictionary against required fields, non-empty rules, and types."""

    capability_id = "output_validate"
    name = "Output Validation"
    version = "1.0.0"
    description = "Performs deterministic assertions on step outputs, verifying schema contracts."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.DETERMINISTIC_ASSERTION
    timeout_seconds = 20
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "required_fields": {"type": "array", "items": {"type": "string"}},
                "non_empty_fields": {"type": "array", "items": {"type": "string"}},
                "type_assertions": {"type": "object"},
            },
            "required": ["data"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "is_valid": {"type": "boolean"},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
                "type_errors": {"type": "array", "items": {"type": "string"}},
                "details": {"type": "string"},
            },
            "required": ["is_valid", "missing_fields", "type_errors"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = input_data.get("data", {})
        if not isinstance(data, dict):
            return {
                "is_valid": False,
                "missing_fields": [],
                "type_errors": [f"Expected dictionary payload, got {type(data).__name__}"],
                "details": "Root payload must be an object",
            }

        required_fields = input_data.get("required_fields", [])
        non_empty_fields = input_data.get("non_empty_fields", [])
        type_assertions = input_data.get("type_assertions", {})

        missing: list[str] = []
        type_errors: list[str] = []

        # 1. Required fields
        for field in required_fields:
            if field not in data:
                missing.append(field)

        # 2. Non-empty check
        for field in non_empty_fields:
            val = data.get(field)
            if val is None or val == "" or val == [] or val == {}:
                missing.append(f"{field} (empty)")

        # 3. Type assertions
        type_map = {
            "str": str,
            "string": str,
            "int": int,
            "integer": int,
            "float": (float, int),
            "number": (float, int),
            "bool": bool,
            "boolean": bool,
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict,
        }
        for field, expected_type_str in type_assertions.items():
            if field in data:
                expected_type = type_map.get(str(expected_type_str).lower())
                if expected_type and not isinstance(data[field], expected_type):
                    type_errors.append(
                        f"Field '{field}' expected {expected_type_str}, got {type(data[field]).__name__}"
                    )

        is_valid = len(missing) == 0 and len(type_errors) == 0
        details = "All assertions passed" if is_valid else f"Failed validation: {len(missing)} missing, {len(type_errors)} type mismatches"

        return {
            "is_valid": is_valid,
            "missing_fields": missing,
            "type_errors": type_errors,
            "details": details,
        }
