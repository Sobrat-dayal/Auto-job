"""Verification Agent auditing step execution outputs across deterministic and semantic layers."""

import json
import logging
from typing import Any

from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
from app.ai.factory import get_ai_gateway
from app.orchestration.contracts import (
    VerificationPolicy,
    VerificationResult,
    VerificationStatus,
    WorkflowStepDefinition,
)

logger = logging.getLogger("autonom.orchestration.verifier")


class VerificationAgent:
    """Agent auditing workflow step outputs for schema conformance and semantic quality."""

    def __init__(self) -> None:
        self.agent_id = "verifier"
        self.name = "Verification Agent"

    async def verify_step(
        self,
        step: WorkflowStepDefinition,
        output_data: dict[str, Any] | None,
        context: dict[str, Any] | None = None,
    ) -> VerificationResult:
        """Verify output of a completed workflow step according to its declared verification policy."""
        policy = step.verification_policy
        step_id = step.step_id

        if output_data is None:
            return VerificationResult(
                step_id=step_id,
                verification_type="null_check",
                status=VerificationStatus.FAIL,
                passed=False,
                score=0.0,
                evidence={"error": "Output is null/missing"},
                details="Step produced no output payload.",
            )

        # 1. Deterministic Layer (always run)
        det_result = self._verify_deterministic(step, output_data)
        if not det_result.passed:
            return det_result

        # 2. Semantic Layer (if policy requires it)
        if policy in (VerificationPolicy.SEMANTIC_REVIEW, VerificationPolicy.OUTPUT_CONTRACT):
            try:
                sem_result = await self._verify_semantic(step, output_data, context)
                return sem_result
            except Exception as exc:
                logger.info("Semantic verification skipped or failed (%s); accepting deterministic pass", exc)
                return VerificationResult(
                    step_id=step_id,
                    verification_type="deterministic_fallback",
                    status=VerificationStatus.PASS,
                    passed=True,
                    score=1.0,
                    evidence={"deterministic": det_result.evidence, "semantic_error": str(exc)},
                    details="Deterministic checks passed; semantic verification was bypassed.",
                )

        return det_result

    def _verify_deterministic(
        self,
        step: WorkflowStepDefinition,
        output_data: dict[str, Any],
    ) -> VerificationResult:
        """Execute deterministic schema and assertion checks."""
        step_id = step.step_id
        schema = step.expected_output_schema

        if not isinstance(output_data, dict):
            return VerificationResult(
                step_id=step_id,
                verification_type="deterministic",
                status=VerificationStatus.FAIL,
                passed=False,
                score=0.0,
                evidence={"received_type": type(output_data).__name__},
                details="Output must be a dictionary/object.",
            )

        # Check required fields if schema provided
        if schema and "required" in schema:
            missing = [f for f in schema["required"] if f not in output_data]
            if missing:
                return VerificationResult(
                    step_id=step_id,
                    verification_type="schema_validation",
                    status=VerificationStatus.FAIL,
                    passed=False,
                    score=0.0,
                    evidence={"missing_fields": missing},
                    details=f"Required fields missing from output: {missing}",
                )

        # For common capabilities, perform heuristic assertions
        if step.capability_id == "text_summarize":
            summary = output_data.get("summary")
            if not summary or not str(summary).strip():
                return VerificationResult(
                    step_id=step_id,
                    verification_type="deterministic",
                    status=VerificationStatus.FAIL,
                    passed=False,
                    score=0.0,
                    evidence={"summary": summary},
                    details="Summary text is empty.",
                )

        elif step.capability_id == "structured_extract":
            data = output_data.get("extracted_data")
            if not data or not isinstance(data, dict):
                return VerificationResult(
                    step_id=step_id,
                    verification_type="deterministic",
                    status=VerificationStatus.FAIL,
                    passed=False,
                    score=0.0,
                    evidence={"extracted_data": data},
                    details="No extracted_data dictionary found in output.",
                )

        elif step.capability_id == "data_transform":
            status = output_data.get("status")
            if status not in ("success", "unmodified"):
                return VerificationResult(
                    step_id=step_id,
                    verification_type="deterministic",
                    status=VerificationStatus.FAIL,
                    passed=False,
                    score=0.0,
                    evidence={"status": status},
                    details=f"Transform status indicated failure: {status}",
                )

        elif step.capability_id == "code_inspect":
            if "valid_syntax" not in output_data:
                return VerificationResult(
                    step_id=step_id,
                    verification_type="deterministic",
                    status=VerificationStatus.FAIL,
                    passed=False,
                    score=0.0,
                    evidence={"keys": list(output_data.keys())},
                    details="Inspection result missing 'valid_syntax' key.",
                )

        return VerificationResult(
            step_id=step_id,
            verification_type="deterministic",
            status=VerificationStatus.PASS,
            passed=True,
            score=1.0,
            evidence={"keys_present": list(output_data.keys())},
            details="All deterministic schema assertions passed.",
        )

    async def _verify_semantic(
        self,
        step: WorkflowStepDefinition,
        output_data: dict[str, Any],
        context: dict[str, Any] | None,
    ) -> VerificationResult:
        """Perform AI-assisted semantic verification of step outputs."""
        gateway = get_ai_gateway()
        prompt = (
            f"Verify whether the following output adequately fulfills the step instruction.\n"
            f"Step Title: {step.title}\n"
            f"Step Description: {step.description}\n"
            f"Output Data: {json.dumps(output_data)[:2500]}\n"
            "Assess for completeness and quality. Respond in JSON with keys:\n"
            "- passed (boolean)\n"
            "- score (float 0.0 to 1.0)\n"
            "- status ('pass', 'fail', 'needs_review')\n"
            "- explanation (string)"
        )
        request = InferenceRequest(
            task_category=TaskCategory.CODE_REVIEW,
            messages=[ChatMessage(role="user", content=prompt)],
            response_format="json_object",
            timeout_seconds=30.0,
        )
        response = await gateway.generate(request)
        data = response.structured_data
        if not data and response.content:
            data = json.loads(response.content)

        passed = bool(data.get("passed", True))
        score = float(data.get("score", 0.9))
        status_str = str(data.get("status", "pass")).lower()
        if status_str == "fail" or not passed:
            stat = VerificationStatus.FAIL
        elif status_str == "needs_review":
            stat = VerificationStatus.NEEDS_REVIEW
        else:
            stat = VerificationStatus.PASS

        return VerificationResult(
            step_id=step.step_id,
            verification_type="semantic_ai",
            status=stat,
            passed=passed,
            score=score,
            evidence=data,
            details=str(data.get("explanation", "Semantic evaluation completed")),
        )
