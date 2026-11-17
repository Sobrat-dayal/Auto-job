"""Structured extraction capability using AI Gateway and regex pattern extractor fallback."""

import json
import logging
import re
from typing import Any

from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
from app.ai.factory import get_ai_gateway
from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.capabilities.structured_extract")


class StructuredExtractCapability(BaseCapability):
    """Extracts structured entities, skills, or fields from unstructured text."""

    capability_id = "structured_extract"
    name = "Structured Entity Extraction"
    version = "1.0.0"
    description = "Parses unstructured text into typed schemas, extracting technical skills, metrics, and entities."
    requires_ai = True
    is_deterministic = False
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 60
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "target_fields": {"type": "array", "items": {"type": "string"}},
                "schema": {"type": "object"},
            },
            "required": ["text"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "extracted_data": {"type": "object"},
                "confidence": {"type": "number"},
                "used_ai": {"type": "boolean"},
            },
            "required": ["extracted_data", "confidence", "used_ai"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = str(input_data.get("text", "")).strip()
        target_fields = input_data.get("target_fields") or [
            "technical_skills",
            "experience_years",
            "job_title",
            "responsibilities",
            "education",
        ]

        # 1. Attempt AI Gateway
        try:
            gateway = get_ai_gateway()
            schema = {
                "type": "object",
                "properties": {f: {"type": "string"} for f in target_fields},
            }
            prompt = (
                f"Extract structured information from the following text for fields: {target_fields}.\n"
                f"Text:\n{text[:5000]}\n"
                "Return JSON with the requested fields. For list-like items (e.g. skills), return an array of strings."
            )
            request = InferenceRequest(
                task_category=TaskCategory.STRUCTURED_EXTRACTION,
                messages=[ChatMessage(role="user", content=prompt)],
                response_format="json_object",
            )
            response = await gateway.generate(request)
            data = response.structured_data
            if not data and response.content:
                try:
                    data = json.loads(response.content)
                except Exception:
                    data = None

            if isinstance(data, dict):
                return {
                    "extracted_data": data,
                    "confidence": 0.92,
                    "used_ai": True,
                }
        except Exception as exc:
            logger.info("AI Gateway extraction bypassed or failed (%s); using regex fallback", exc)

        # 2. Deterministic pattern fallback
        extracted: dict[str, Any] = {}

        # Experience pattern
        exp_match = re.search(r"(\d+)\+?\s*(?:-\s*(\d+))?\s*(?:years?|yrs)", text, re.IGNORECASE)
        if exp_match:
            min_y = exp_match.group(1)
            max_y = exp_match.group(2)
            extracted["experience_years"] = f"{min_y}-{max_y} years" if max_y else f"{min_y}+ years"
        else:
            extracted["experience_years"] = "Not explicitly specified"

        # Common tech skills lexicon
        tech_lexicon = [
            "python", "rust", "react", "typescript", "javascript", "c++", "go", "sql",
            "docker", "kubernetes", "aws", "gcp", "azure", "fastapi", "linux", "git",
            "node.js", "pytorch", "tensorflow", "graphql", "tailwind", "vite", "sqlite",
            "postgresql", "redis", "tauri", "grpc", "ci/cd", "rest api", "html5", "css3"
        ]
        text_lower = text.lower()
        found_skills = [
            s.title() if len(s) > 3 else s.upper()
            for s in tech_lexicon
            if re.search(r"\b" + re.escape(s) + r"\b", text_lower)
        ]
        extracted["technical_skills"] = found_skills

        # Education
        edu_match = re.search(r"(bachelor|master|phd|b\.s|m\.s|degree)\s*(?:of|in)?\s*([a-zA-Z\s]+)?", text_lower)
        if edu_match:
            extracted["education"] = edu_match.group(0).strip().title()
        else:
            extracted["education"] = "Degree in Computer Science or related field preferred"

        # Job title heuristic
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        extracted["job_title"] = lines[0] if lines else "Software Engineer"

        # Responsibilities
        bullet_lines = [
            re.sub(r"^[-*•]\s*", "", line).strip()
            for line in lines
            if re.match(r"^[-*•]\s+", line)
        ]
        extracted["responsibilities"] = bullet_lines[:5] if bullet_lines else lines[1:4]

        return {
            "extracted_data": extracted,
            "confidence": 0.85,
            "used_ai": False,
        }
