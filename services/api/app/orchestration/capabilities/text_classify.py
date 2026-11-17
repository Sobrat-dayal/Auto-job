"""Text classification capability with category scoring and deterministic fallback."""

import json
import logging
import re
from typing import Any

from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
from app.ai.factory import get_ai_gateway
from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.capabilities.text_classify")


class TextClassifyCapability(BaseCapability):
    """Classifies text into specified candidate categories."""

    capability_id = "text_classify"
    name = "Text Classification"
    version = "1.0.0"
    description = "Categorizes text into predefined classes with confidence metrics."
    requires_ai = True
    is_deterministic = False
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 45
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "categories": {"type": "array", "items": {"type": "string"}},
                "multi_label": {"type": "boolean", "default": False},
            },
            "required": ["text", "categories"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "classification": {"type": "string"},
                "confidence": {"type": "number"},
                "scores": {"type": "object"},
                "used_ai": {"type": "boolean"},
            },
            "required": ["classification", "confidence", "scores", "used_ai"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = str(input_data.get("text", "")).strip()
        categories = [str(c).strip() for c in input_data.get("categories", []) if str(c).strip()]
        if not categories:
            categories = ["General", "Technical", "Operations", "Administrative"]

        # 1. Attempt AI Gateway
        try:
            gateway = get_ai_gateway()
            schema = {
                "type": "object",
                "properties": {
                    "primary_category": {"type": "string", "enum": categories},
                    "confidence": {"type": "number"},
                    "scores": {"type": "object"},
                },
                "required": ["primary_category", "confidence"],
            }
            prompt = (
                f"Classify the following text into exactly one of these categories: {categories}.\n"
                f"Text:\n{text[:4000]}\n"
                "Respond in valid JSON with keys: primary_category, confidence (0.0 to 1.0), and scores (dict)."
            )
            request = InferenceRequest(
                task_category=TaskCategory.CLASSIFICATION,
                messages=[ChatMessage(role="user", content=prompt)],
                response_format="json_object",
                json_schema=schema,
            )
            response = await gateway.generate(request)
            data = response.structured_data
            if not data and response.content:
                try:
                    data = json.loads(response.content)
                except Exception:
                    data = None

            if isinstance(data, dict) and "primary_category" in data:
                cat = str(data["primary_category"])
                conf = float(data.get("confidence", 0.9))
                scores = data.get("scores", {cat: conf})
                return {
                    "classification": cat,
                    "confidence": conf,
                    "scores": scores,
                    "used_ai": True,
                }
        except Exception as exc:
            logger.info("AI Gateway classification bypassed or failed (%s); using keyword fallback", exc)

        # 2. Deterministic keyword fallback
        words = re.findall(r"\w+", text.lower())
        scores: dict[str, float] = {}
        for cat in categories:
            cat_words = set(re.findall(r"\w+", cat.lower()))
            matches = sum(1 for w in words if w in cat_words)
            scores[cat] = float(matches)

        total_matches = sum(scores.values())
        if total_matches > 0:
            norm_scores = {c: round(cnt / total_matches, 3) for c, cnt in scores.items()}
            best_cat = max(norm_scores, key=lambda c: norm_scores[c])
            conf = norm_scores[best_cat]
        else:
            norm_scores = {c: round(1.0 / len(categories), 3) for c in categories}
            best_cat = categories[0]
            conf = 0.5

        return {
            "classification": best_cat,
            "confidence": conf,
            "scores": norm_scores,
            "used_ai": False,
        }
