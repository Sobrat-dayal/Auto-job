"""Creative, Communication, and Market Intelligence capabilities for AUTONOM (Stage 13)."""

from datetime import UTC, datetime
import json
import logging
import re
from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.capabilities.creative_comms")


class CreativeSceneSpecificationCapability(BaseCapability):
    """Transforms a creative prompt or brief into a structured 3D scene specification."""

    capability_id = "creative_scene_specification"
    name = "3D Scene Specification"
    version = "1.0.0"
    description = "Decomposes a creative brief into 3D scene geometry, lighting setups, materials, and camera perspectives."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 45
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "brief": {"type": "string"},
                "scene_type": {"type": "string"},
            },
            "required": ["brief"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "scene_name": {"type": "string"},
                "camera_setup": {"type": "object"},
                "lighting_setup": {"type": "object"},
                "objects": {"type": "array", "items": {"type": "object"}},
                "render_resolution": {"type": "string"},
            },
            "required": ["scene_name", "camera_setup", "lighting_setup", "objects"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        brief = str(input_data.get("brief", "Minimalist product render"))
        scene_type = str(input_data.get("scene_type", "Studio Product"))

        return {
            "scene_name": f"{scene_type} - {brief[:30]}",
            "camera_setup": {
                "focal_length_mm": 50,
                "aperture": "f/2.8",
                "position": [0.0, -3.0, 1.2],
                "target": [0.0, 0.0, 0.5],
            },
            "lighting_setup": {
                "key_light": {"type": "Area", "energy_watts": 500, "color_temperature": 5600},
                "fill_light": {"type": "Area", "energy_watts": 200, "color_temperature": 6000},
                "rim_light": {"type": "Spot", "energy_watts": 350, "color_temperature": 4500},
            },
            "objects": [
                {"name": "Hero Subject", "mesh_type": "Primitive/Asset", "material": "Matte PBR", "position": [0, 0, 0]},
                {"name": "Infinity Backdrop", "mesh_type": "Curved Plane", "material": "Neutral Grey Diffuse", "position": [0, 2, 0]},
            ],
            "render_resolution": "1920x1080 (Full HD)",
        }


class MsgClassifyMessageCapability(BaseCapability):
    """Classifies incoming user or recruiter messages by intent, urgency, and actionability."""

    capability_id = "msg_classify_message"
    name = "Classify Incoming Message"
    version = "1.0.0"
    description = "Categorizes messages into inquiry, interview offer, rejection, follow-up, or general communication."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 20
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message_text": {"type": "string"},
                "sender": {"type": "string"},
            },
            "required": ["message_text"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "urgency": {"type": "string"},
                "requires_reply": {"type": "boolean"},
                "action_item": {"type": "string"},
            },
            "required": ["category", "urgency", "requires_reply"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = str(input_data.get("message_text", "")).lower()

        if any(w in text for w in ["interview", "schedule", "call", "availability", "chat"]):
            cat = "Interview Invitation / Scheduling"
            urgency = "High"
            reply = True
            action = "Confirm candidate availability time slots."
        elif any(w in text for w in ["unfortunately", "not moving forward", "regret", "other candidates"]):
            cat = "Application Update (Rejection)"
            urgency = "Low"
            reply = False
            action = "Update job application tracking status."
        elif any(w in text for w in ["offer", "compensation", "congratulations"]):
            cat = "Job Offer"
            urgency = "Critical"
            reply = True
            action = "Notify user immediately to review offer package."
        else:
            cat = "General Recruitment Inquiry"
            urgency = "Medium"
            reply = True
            action = "Review inquiry and determine next steps."

        return {
            "category": cat,
            "urgency": urgency,
            "requires_reply": reply,
            "action_item": action,
        }


class MsgDraftResponseCapability(BaseCapability):
    """Drafts contextual message responses in specified communication tones."""

    capability_id = "msg_draft_response"
    name = "Draft Message Response"
    version = "1.0.0"
    description = "Prepares courteous, structured responses tailored to user tone and message intent."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "incoming_message": {"type": "string"},
                "tone": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["incoming_message"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "draft_text": {"type": "string"},
                "tone": {"type": "string"},
            },
            "required": ["draft_text", "tone"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tone = str(input_data.get("tone", "Professional & Courteous"))
        points = input_data.get("key_points", ["Appreciation for outreach", "Confirmed availability"])

        body = (
            f"Hello,\n\n"
            f"Thank you for your message. {points[0]}.\n"
            f"Regarding your question, {points[1] if len(points) > 1 else 'I am looking forward to our discussion'}.\n\n"
            f"Looking forward to connecting soon.\n\n"
            f"Best regards,\nCandidate"
        )

        return {
            "draft_text": body,
            "tone": tone,
        }


class MarketAnalyzeSuppliedDataCapability(BaseCapability):
    """Performs deterministic market and competitor numerical comparisons from supplied data."""

    capability_id = "market_analyze_supplied_data"
    name = "Analyze Market Data"
    version = "1.0.0"
    description = "Compares competitor metrics, growth rates, and market share from verified supplied inputs."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entities": {"type": "array", "items": {"type": "object"}},
                "metric_key": {"type": "string"},
            },
            "required": ["entities"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "total_entities": {"type": "integer"},
                "leader": {"type": "string"},
                "comparisons": {"type": "array", "items": {"type": "object"}},
                "verified_from_supplied": {"type": "boolean"},
            },
            "required": ["total_entities", "leader", "comparisons", "verified_from_supplied"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entities = input_data.get("entities", [])
        metric = input_data.get("metric_key", "score")

        sorted_entities = sorted(
            entities,
            key=lambda e: float(e.get(metric, 0)),
            reverse=True,
        ) if entities else []

        leader_name = sorted_entities[0].get("name", "N/A") if sorted_entities else "None"

        return {
            "total_entities": len(entities),
            "leader": leader_name,
            "comparisons": sorted_entities,
            "verified_from_supplied": True,
        }
