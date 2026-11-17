"""Text summarization capability with AI Gateway execution and extractive fallback."""

import logging
import re
from typing import Any

from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
from app.ai.factory import get_ai_gateway
from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.capabilities.text_summarize")


class TextSummarizeCapability(BaseCapability):
    """Summarizes input text with length and focus constraints."""

    capability_id = "text_summarize"
    name = "Text Summarization"
    version = "1.0.0"
    description = "Condenses text while preserving core requirements, responsibilities, or skills."
    requires_ai = True
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 60
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input text to summarize"},
                "focus": {"type": "string", "description": "Specific focus area (e.g. responsibilities)"},
                "max_length": {"type": "integer", "default": 200},
                "bullet_points": {"type": "boolean", "default": False},
            },
            "required": ["text"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "sentence_count": {"type": "integer"},
                "used_ai": {"type": "boolean"},
                "focus": {"type": "string"},
            },
            "required": ["summary", "used_ai"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = str(input_data.get("text", "")).strip()
        if not text:
            return {"summary": "", "sentence_count": 0, "used_ai": False, "focus": None}

        focus = input_data.get("focus")
        max_length = int(input_data.get("max_length", 200))
        bullet_points = bool(input_data.get("bullet_points", False))

        # 1. Attempt AI Gateway generation
        try:
            gateway = get_ai_gateway()
            sys_prompt = "You are a concise executive summarizer. Produce an accurate, dense summary."
            user_msg = f"Summarize the following text (max {max_length} words)."
            if focus:
                user_msg += f" Focus especially on: {focus}."
            if bullet_points:
                user_msg += " Output as clean bullet points starting with '-'."
            user_msg += f"\n\nText:\n{text[:6000]}"

            request = InferenceRequest(
                task_category=TaskCategory.SUMMARIZATION,
                system_prompt=sys_prompt,
                messages=[ChatMessage(role="user", content=user_msg)],
                max_tokens=max_length * 2,
            )
            response = await gateway.generate(request)
            if response.content and response.content.strip():
                summary = response.content.strip()
                sentences = re.split(r"(?<=[.!?])\s+", summary)
                return {
                    "summary": summary,
                    "sentence_count": len(sentences),
                    "used_ai": True,
                    "focus": focus,
                }
        except Exception as exc:
            logger.info("AI Gateway summarization bypassed or failed (%s); using extractive fallback", exc)

        # 2. Deterministic extractive fallback
        sentences = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", text) if len(s.strip()) > 15]
        if not sentences:
            sentences = [text[:200]]

        if focus:
            focus_words = set(re.findall(r"\w+", focus.lower()))
            def score(sent: str) -> int:
                words = set(re.findall(r"\w+", sent.lower()))
                return len(words.intersection(focus_words))
            sentences.sort(key=score, reverse=True)

        selected = sentences[: max(1, min(len(sentences), 4))]
        if bullet_points:
            summary = "\n".join(f"- {s}" for s in selected)
        else:
            summary = " ".join(selected)

        return {
            "summary": summary,
            "sentence_count": len(selected),
            "used_ai": False,
            "focus": focus,
        }
