"""Shared workflow context and input binding resolution engine."""

import copy
import re
from typing import Any


class WorkflowContext:
    """Manages shared execution context across workflow steps and resolves input bindings."""

    def __init__(
        self,
        workflow_id: str,
        initial_inputs: dict[str, Any] | None = None,
    ) -> None:
        self.workflow_id = workflow_id
        self.inputs: dict[str, Any] = initial_inputs or {}
        # step_id -> step output payload dictionary
        self.step_outputs: dict[str, dict[str, Any]] = {}
        # step_id -> metadata (agent, execution time, tokens, cost)
        self.step_metadata: dict[str, dict[str, Any]] = {}
        # Global workflow variables
        self.variables: dict[str, Any] = {}

    def set_step_output(
        self,
        step_id: str,
        output_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store output dictionary and metadata for a completed step."""
        self.step_outputs[step_id] = copy.deepcopy(output_data)
        if metadata:
            self.step_metadata[step_id] = copy.deepcopy(metadata)

    def get_step_output(self, step_id: str) -> dict[str, Any] | None:
        """Retrieve output dictionary for a step."""
        return self.step_outputs.get(step_id)

    def resolve_bindings(self, bindings: dict[str, Any]) -> dict[str, Any]:
        """Resolve all bindings in an input dictionary recursively."""
        resolved: dict[str, Any] = {}
        for key, val in bindings.items():
            resolved[key] = self.resolve_value(val)
        return resolved

    def resolve_value(self, val: Any) -> Any:
        """Resolve a single value (string, dict, list, or primitive)."""
        if isinstance(val, dict):
            return {k: self.resolve_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [self.resolve_value(item) for item in val]
        elif isinstance(val, str):
            return self._resolve_string_binding(val)
        return val

    def _resolve_string_binding(self, text: str) -> Any:
        """Resolve '{{path}}' expressions within a string."""
        pattern = r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}"
        matches = list(re.finditer(pattern, text))
        if not matches:
            return text

        # Exact single match covering entire string -> return typed value directly
        if len(matches) == 1 and matches[0].group(0) == text.strip():
            path = matches[0].group(1)
            return self._lookup_path(path)

        # Embedded string interpolation
        def repl(match: re.Match) -> str:
            path = match.group(1)
            resolved = self._lookup_path(path)
            return str(resolved) if resolved is not None else ""

        return re.sub(pattern, repl, text)

    def _lookup_path(self, path: str) -> Any:
        """Lookup a dot-notated path in context (e.g. 'input.job_description' or 'step_1.summary')."""
        parts = path.split(".")
        root_key = parts[0]

        if root_key == "input" or root_key == "inputs":
            curr = self.inputs
            lookup_parts = parts[1:]
        elif root_key in self.step_outputs:
            curr = self.step_outputs[root_key]
            lookup_parts = parts[1:]
        elif root_key in self.variables:
            curr = self.variables[root_key]
            lookup_parts = parts[1:]
        else:
            return None

        for part in lookup_parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            elif isinstance(curr, list) and part.isdigit() and int(part) < len(curr):
                curr = curr[int(part)]
            else:
                return None

        return curr

    def to_dict(self) -> dict[str, Any]:
        """Serialize context snapshot."""
        return {
            "inputs": self.inputs,
            "step_outputs": self.step_outputs,
            "variables": self.variables,
        }
