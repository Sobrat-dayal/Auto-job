"""Text comparison capability computing similarity, line diffs, and overlap metrics."""

import difflib
import re
from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy


class TextCompareCapability(BaseCapability):
    """Compares two text strings, computing similarity metrics and unified diffs."""

    capability_id = "text_compare"
    name = "Text Comparison"
    version = "1.0.0"
    description = "Computes sequence similarity ratio, token intersection, and line diffs between texts."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.DETERMINISTIC_ASSERTION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text_a": {"type": "string"},
                "text_b": {"type": "string"},
            },
            "required": ["text_a", "text_b"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "similarity_ratio": {"type": "number"},
                "diff_lines": {"type": "array", "items": {"type": "string"}},
                "common_terms": {"type": "array", "items": {"type": "string"}},
                "length_delta": {"type": "integer"},
            },
            "required": ["similarity_ratio", "diff_lines", "common_terms", "length_delta"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text_a = str(input_data.get("text_a", ""))
        text_b = str(input_data.get("text_b", ""))

        matcher = difflib.SequenceMatcher(None, text_a, text_b)
        ratio = round(matcher.ratio(), 4)

        lines_a = text_a.splitlines(keepends=True)
        lines_b = text_b.splitlines(keepends=True)
        diff = list(difflib.unified_diff(lines_a, lines_b, fromfile="text_a", tofile="text_b", n=1))

        words_a = set(re.findall(r"\w+", text_a.lower()))
        words_b = set(re.findall(r"\w+", text_b.lower()))
        common = sorted(list(words_a.intersection(words_b)))

        return {
            "similarity_ratio": ratio,
            "diff_lines": [line.rstrip("\n") for line in diff[:50]],
            "common_terms": common[:30],
            "length_delta": len(text_b) - len(text_a),
        }
