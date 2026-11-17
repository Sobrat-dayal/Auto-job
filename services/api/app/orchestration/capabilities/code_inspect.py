"""Code inspection capability for deterministic AST syntax, structural analysis, and metrics."""

import ast
from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy


class CodeInspectCapability(BaseCapability):
    """Inspects Python source code for syntax errors, AST structure, and complexity."""

    capability_id = "code_inspect"
    name = "Code Inspection"
    version = "1.0.0"
    description = "Inspects source code for syntax validity, functions, classes, and structural metrics."
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
                "code": {"type": "string"},
                "language": {"type": "string", "default": "python"},
            },
            "required": ["code"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "valid_syntax": {"type": "boolean"},
                "syntax_error": {"type": ["string", "null"]},
                "function_count": {"type": "integer"},
                "class_count": {"type": "integer"},
                "line_count": {"type": "integer"},
                "complexity_score": {"type": "integer"},
            },
            "required": ["valid_syntax", "function_count", "class_count", "line_count"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        code = str(input_data.get("code", ""))
        language = str(input_data.get("language", "python")).lower()
        lines = code.splitlines()

        if language != "python":
            return {
                "valid_syntax": True,
                "syntax_error": None,
                "function_count": 0,
                "class_count": 0,
                "line_count": len(lines),
                "complexity_score": 1,
            }

        try:
            tree = ast.parse(code)
            functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

            # Cyclomatic complexity heuristic: count branches (if, for, while, try, except, boolean ops)
            branch_nodes = [
                n for n in ast.walk(tree)
                if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.BoolOp))
            ]
            complexity = 1 + len(branch_nodes)

            return {
                "valid_syntax": True,
                "syntax_error": None,
                "function_count": len(functions),
                "class_count": len(classes),
                "line_count": len(lines),
                "complexity_score": complexity,
            }
        except SyntaxError as err:
            return {
                "valid_syntax": False,
                "syntax_error": f"Line {err.lineno}: {err.msg}",
                "function_count": 0,
                "class_count": 0,
                "line_count": len(lines),
                "complexity_score": 0,
            }
