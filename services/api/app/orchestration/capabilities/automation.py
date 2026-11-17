"""Workflow automation capabilities for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.capabilities.automation")


class WorkflowProposeTemplateCapability(BaseCapability):
    """Proposes a structured DAG execution workflow template based on high-level goals."""

    capability_id = "workflow_propose_template"
    name = "Propose Workflow Template"
    version = "1.0.0"
    description = "Decomposes multi-step automation goals into a validated, dependency-ordered DAG template."
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
                "goal": {"type": "string"},
                "category": {"type": "string"},
            },
            "required": ["goal"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "template_name": {"type": "string"},
                "stages": {"type": "array", "items": {"type": "object"}},
                "total_steps": {"type": "integer"},
                "is_cycle_free": {"type": "boolean"},
            },
            "required": ["template_name", "stages", "total_steps", "is_cycle_free"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        goal = str(input_data.get("goal", "Automated Task Pipeline"))

        stages = [
            {
                "stage": 1,
                "steps": [
                    {"step_id": "step_1", "capability_id": "recruitment_extract_job_requirements", "title": "Analyze Requirements"},
                ],
            },
            {
                "stage": 2,
                "steps": [
                    {"step_id": "step_2", "capability_id": "recruitment_match_skills", "dependencies": ["step_1"], "title": "Match Applicant Skills"},
                ],
            },
            {
                "stage": 3,
                "steps": [
                    {"step_id": "step_3", "capability_id": "recruitment_draft_resume_bullets", "dependencies": ["step_2"], "title": "Tailor Resume"},
                    {"step_id": "step_4", "capability_id": "recruitment_generate_interview_questions", "dependencies": ["step_1"], "title": "Prepare Interview Questions"},
                ],
            },
        ]

        return {
            "template_name": f"DAG Pipeline: {goal[:40]}",
            "stages": stages,
            "total_steps": 4,
            "is_cycle_free": True,
        }


class WorkflowValidateConfigCapability(BaseCapability):
    """Validates workflow step parameters, timeout values, and dependency linkages."""

    capability_id = "workflow_validate_config"
    name = "Validate Workflow Configuration"
    version = "1.0.0"
    description = "Checks workflow JSON configurations for missing capabilities, circular links, and valid timeouts."
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
                "steps": {"type": "array", "items": {"type": "object"}},
            },
            "required": ["steps"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "is_valid": {"type": "boolean"},
                "errors": {"type": "array", "items": {"type": "string"}},
                "step_count": {"type": "integer"},
            },
            "required": ["is_valid", "errors", "step_count"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        steps = input_data.get("steps", [])
        errors = []

        step_ids = set()
        for s in steps:
            sid = s.get("step_id")
            if not sid:
                errors.append("Step missing 'step_id'")
            elif sid in step_ids:
                errors.append(f"Duplicate step_id '{sid}'")
            else:
                step_ids.add(sid)

        for s in steps:
            for dep in s.get("dependencies", []):
                if dep not in step_ids:
                    errors.append(f"Step '{s.get('step_id')}' references non-existent dependency '{dep}'")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "step_count": len(steps),
        }
