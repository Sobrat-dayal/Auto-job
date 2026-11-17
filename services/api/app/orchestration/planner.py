"""Planning Agent responsible for goal decomposition, structured DAG generation, and plan versioning."""

import json
import logging
from typing import Any

from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
from app.ai.factory import get_ai_gateway
from app.orchestration.contracts import (
    PriorityLevel,
    VerificationPolicy,
    WorkflowPlan,
    WorkflowStepDefinition,
)
from app.orchestration.graph import DependencyGraph

logger = logging.getLogger("autonom.orchestration.planner")


class PlanningAgent:
    """Intelligent Planning Agent decomposing user goals into validated dependency DAG plans."""

    def __init__(self) -> None:
        self.agent_id = "planner"
        self.name = "Planning Agent"

    async def create_plan(
        self,
        workflow_id: str,
        goal: str,
        constraints: dict[str, Any] | None = None,
        priority: PriorityLevel = PriorityLevel.NORMAL,
        version: int = 1,
    ) -> WorkflowPlan:
        """Generate a valid, acyclic WorkflowPlan from a user goal and constraints."""
        constraints = constraints or {}
        logger.info("PlanningAgent generating plan for workflow '%s' (v%d): %s", workflow_id, version, goal[:100])

        steps: list[WorkflowStepDefinition] = []

        # 1. Check if AI Gateway is available and has models to generate dynamic plan
        try:
            steps = await self._generate_plan_via_ai(goal, constraints)
        except Exception as exc:
            logger.info("AI Gateway planning skipped or failed (%s); using deterministic planner template", exc)
            steps = []

        # 2. Fallback to specialized deterministic goal planner if AI output was empty or invalid
        if not steps:
            steps = self._generate_deterministic_plan(goal, constraints)

        # 3. Validate DAG and detect cycles
        try:
            graph = DependencyGraph(steps)
            logger.info(
                "Plan validated successfully: %d steps, topological order: %s",
                len(steps),
                graph.topological_order,
            )
        except ValueError as err:
            logger.error("Generated plan failed DAG cycle check: %s. Sanitizing dependencies...", err)
            steps = self._sanitize_steps_to_linear(steps)
            DependencyGraph(steps)  # verify sanitized

        return WorkflowPlan(
            workflow_id=workflow_id,
            version=version,
            goal=goal,
            steps=steps,
            success_criteria=[
                "All workflow step dependencies executed successfully",
                "All step outputs verified against schemas",
                "Final workflow output artifact compiled and validated",
            ],
            max_duration_seconds=300,
            max_total_steps=len(steps),
            max_parallel_steps=4,
        )

    async def _generate_plan_via_ai(
        self,
        goal: str,
        constraints: dict[str, Any],
    ) -> list[WorkflowStepDefinition]:
        """Ask AI Gateway to decompose goal into structured steps."""
        gateway = get_ai_gateway()
        system_prompt = (
            "You are an expert autonomous system planner. Decompose the user's goal into discrete executable steps.\n"
            "Available capabilities: text_summarize, text_classify, structured_extract, text_compare, data_transform, output_validate, code_inspect.\n"
            "Each step MUST have: step_id, title, capability_id, dependencies (list of prior step_ids), and input_bindings.\n"
            "Ensure the dependency graph is an ACYCLIC directed graph (no loops)."
        )
        user_prompt = (
            f"Goal: {goal}\nConstraints: {json.dumps(constraints)}\n"
            "Return valid JSON with key 'steps' as an array of step objects."
        )

        request = InferenceRequest(
            task_category=TaskCategory.PLANNING,
            system_prompt=system_prompt,
            messages=[ChatMessage(role="user", content=user_prompt)],
            response_format="json_object",
            timeout_seconds=45.0,
        )
        response = await gateway.generate(request)
        data = response.structured_data
        if not data and response.content:
            data = json.loads(response.content)

        if not isinstance(data, dict) or "steps" not in data or not isinstance(data["steps"], list):
            return []

        raw_steps = data["steps"]
        steps: list[WorkflowStepDefinition] = []
        for i, s in enumerate(raw_steps):
            step_id = str(s.get("step_id") or f"step_{i+1}")
            steps.append(
                WorkflowStepDefinition(
                    step_id=step_id,
                    title=str(s.get("title", f"Step {i+1}")),
                    description=str(s.get("description", "")),
                    capability_id=str(s.get("capability_id", "data_transform")),
                    dependencies=[str(d) for d in s.get("dependencies", []) if str(d) != step_id],
                    input_bindings=s.get("input_bindings", {}),
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                )
            )

        return steps

    def _generate_deterministic_plan(
        self,
        goal: str,
        constraints: dict[str, Any],
    ) -> list[WorkflowStepDefinition]:
        """High-fidelity deterministic decomposition tailored to multi-agent specialist workflows."""
        goal_lower = goal.lower()

        # 1. Full Multi-Agent Recruitment & Tailoring Collaboration Workflow (Stage 13)
        if (
            ("interview" in goal_lower and "resume" in goal_lower)
            or ("verified skills" in goal_lower)
            or ("preparation plan" in goal_lower)
            or ("compare" in goal_lower and "skills" in goal_lower and "interview" in goal_lower)
        ):
            return [
                WorkflowStepDefinition(
                    step_id="step_extract",
                    title="Extract Role Requirements",
                    description="Extract hard/soft skills, required experience, and credentials from job posting.",
                    capability_id="recruitment_extract_job_requirements",
                    dependencies=[],
                    input_bindings={
                        "job_description": "{{input.job_description}}",
                        "role_title": "{{input.role_title}}",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_match",
                    title="Match Verified Applicant Skills",
                    description="Perform grounded comparison between extracted job requirements and verified applicant profile.",
                    capability_id="recruitment_match_skills",
                    dependencies=["step_extract"],
                    input_bindings={
                        "required_skills": "{{step_extract.required_skills}}",
                        "applicant_skills": "{{input.applicant_skills}}",
                        "role_title": "{{step_extract.role_title}}",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_resume",
                    title="Draft Tailored Resume Achievements",
                    description="Draft grounded, impact-oriented resume bullet points highlighting matched skills.",
                    capability_id="recruitment_draft_resume_bullets",
                    dependencies=["step_match"],
                    input_bindings={
                        "matched_skills": "{{step_match.matched_skills}}",
                        "verified_experience": "{{input.verified_experience}}",
                        "target_role": "{{step_extract.role_title}}",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_interview",
                    title="Generate Targeted Interview Questions",
                    description="Generate technical drills, behavioral questions, and preparation study guide.",
                    capability_id="recruitment_generate_interview_questions",
                    dependencies=["step_extract"],
                    input_bindings={
                        "role_title": "{{step_extract.role_title}}",
                        "required_skills": "{{step_extract.required_skills}}",
                        "job_description": "{{input.job_description}}",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_report",
                    title="Synthesize Comprehensive Recruitment Report",
                    description="Consolidate skill match analysis, tailored resume bullets, and interview plan into structured report.",
                    capability_id="doc_draft_report",
                    dependencies=["step_match", "step_resume", "step_interview"],
                    input_bindings={
                        "title": "Comprehensive Candidate Assessment & Tailoring Report",
                        "findings": {
                            "match_summary": "{{step_match.summary}}",
                            "recommendation": "{{step_match.recommendation}}",
                            "tailored_bullets": "{{step_resume.suggested_bullets}}",
                            "interview_questions": "{{step_interview.technical_questions}}",
                        },
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_validate",
                    title="Validate Consolidated Report",
                    description="Verify that the generated report meets completeness and non-empty criteria.",
                    capability_id="output_validate",
                    dependencies=["step_report"],
                    input_bindings={
                        "data": {
                            "title": "{{step_report.title}}",
                            "word_count": "{{step_report.word_count}}",
                        },
                        "required_fields": ["title", "word_count"],
                    },
                    verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
                ),
            ]

        # 2. Multi-Agent Coding & Technical Review Collaboration Workflow (Stage 13)
        if (
            ("python function" in goal_lower or "bugs" in goal_lower)
            and ("test cases" in goal_lower or "technical review" in goal_lower)
        ):
            return [
                WorkflowStepDefinition(
                    step_id="step_explain",
                    title="Explain Code Architecture & Complexity",
                    description="Analyze code structure, algorithm flow, and computational complexity.",
                    capability_id="code_explain",
                    dependencies=[],
                    input_bindings={
                        "code": "{{input.source_code}}",
                        "language": "python",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_review",
                    title="Static Review & Bug Identification",
                    description="Identify potential runtime defects, security risks, and refactoring opportunities.",
                    capability_id="code_review_static",
                    dependencies=["step_explain"],
                    input_bindings={
                        "code": "{{input.source_code}}",
                        "language": "{{step_explain.language}}",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_tests",
                    title="Generate Unit Test Cases",
                    description="Generate comprehensive unit test suite covering nominal and edge cases.",
                    capability_id="code_generate_tests",
                    dependencies=["step_explain"],
                    input_bindings={
                        "code": "{{input.source_code}}",
                        "framework": "pytest",
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_report",
                    title="Compile Technical Code Review Report",
                    description="Synthesize architecture summary, review findings, and test suite into structured report.",
                    capability_id="doc_draft_report",
                    dependencies=["step_review", "step_tests"],
                    input_bindings={
                        "title": "Technical Code Review & Quality Assessment",
                        "findings": {
                            "architecture_summary": "{{step_explain.summary}}",
                            "review_quality": "{{step_review.overall_quality}}",
                            "test_cases_count": "{{step_tests.test_cases_count}}",
                        },
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_validate",
                    title="Audit Review Artifact Quality",
                    description="Assert non-zero word count and presence of test cases.",
                    capability_id="output_validate",
                    dependencies=["step_report"],
                    input_bindings={
                        "data": {
                            "title": "{{step_report.title}}",
                            "word_count": "{{step_report.word_count}}",
                        },
                        "required_fields": ["title", "word_count"],
                    },
                    verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
                ),
            ]

        # Job analysis, recruitment, or structured text analysis workflow
        if any(w in goal_lower for w in ["job", "resume", "extract", "report", "skill", "requirement", "description"]):
            return [
                WorkflowStepDefinition(
                    step_id="step_extract",
                    title="Extract Skills & Experience Requirements",
                    description="Extract technical skills, required experience, education, and job title from the job description.",
                    capability_id="structured_extract",
                    dependencies=[],
                    input_bindings={"text": "{{input.job_description}}"},
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_summarize",
                    title="Summarize Role Responsibilities",
                    description="Generate an executive summary highlighting core day-to-day responsibilities and duties.",
                    capability_id="text_summarize",
                    dependencies=[],
                    input_bindings={
                        "text": "{{input.job_description}}",
                        "focus": "responsibilities and role expectations",
                        "bullet_points": True,
                    },
                    verification_policy=VerificationPolicy.OUTPUT_CONTRACT,
                ),
                WorkflowStepDefinition(
                    step_id="step_classify",
                    title="Classify Role Domain & Seniority",
                    description="Determine the technical specialization domain of the opportunity.",
                    capability_id="text_classify",
                    dependencies=[],
                    input_bindings={
                        "text": "{{input.job_description}}",
                        "categories": [
                            "Full Stack Engineering",
                            "Backend Systems",
                            "Frontend & Desktop UI",
                            "AI & Machine Learning",
                            "DevOps & Cloud Infrastructure",
                        ],
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_report",
                    title="Compile Structured Analysis Report",
                    description="Combine extracted skills, role summary, and domain classifications into a unified executive report.",
                    capability_id="data_transform",
                    dependencies=["step_extract", "step_summarize", "step_classify"],
                    input_bindings={
                        "operation": "format_markdown_report",
                        "data": {
                            "title": "Autonomous Job Requirement Analysis",
                            "job_title": "{{step_extract.extracted_data.job_title}}",
                            "skills": "{{step_extract.extracted_data.technical_skills}}",
                            "experience": "{{step_extract.extracted_data.experience_years}}",
                            "summary": "{{step_summarize.summary}}",
                        },
                    },
                    verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
                ),
                WorkflowStepDefinition(
                    step_id="step_validate",
                    title="Validate Final Report Artifact",
                    description="Verify that the generated report meets all schema requirements and non-empty criteria.",
                    capability_id="output_validate",
                    dependencies=["step_report"],
                    input_bindings={
                        "data": "{{step_report.transformed_data}}",
                        "required_fields": ["report_markdown", "title"],
                        "non_empty_fields": ["report_markdown"],
                    },
                    verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
                ),
            ]

        # Code inspection or analysis workflow
        if any(w in goal_lower for w in ["code", "inspect", "ast", "syntax"]):
            return [
                WorkflowStepDefinition(
                    step_id="step_inspect",
                    title="Inspect Source Code AST",
                    description="Perform deterministic AST syntax inspection and measure cyclomatic complexity.",
                    capability_id="code_inspect",
                    dependencies=[],
                    input_bindings={"code": "{{input.source_code}}", "language": "python"},
                    verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
                ),
                WorkflowStepDefinition(
                    step_id="step_validate",
                    title="Validate Inspection Results",
                    description="Verify syntax validity and non-zero node metrics.",
                    capability_id="output_validate",
                    dependencies=["step_inspect"],
                    input_bindings={
                        "data": "{{step_inspect}}",
                        "required_fields": ["valid_syntax", "function_count", "line_count"],
                    },
                    verification_policy=VerificationPolicy.DETERMINISTIC_ASSERTION,
                ),
            ]

        # Generic multi-step text workflow
        return [
            WorkflowStepDefinition(
                step_id="step_summarize",
                title="Summarize Goal Input",
                description="Extract main points and themes from the target text.",
                capability_id="text_summarize",
                dependencies=[],
                input_bindings={"text": "{{input.text}}"},
                verification_policy=VerificationPolicy.OUTPUT_CONTRACT,
            ),
            WorkflowStepDefinition(
                step_id="step_report",
                title="Transform Summary into Output",
                description="Format summary into structured data envelope.",
                capability_id="data_transform",
                dependencies=["step_summarize"],
                input_bindings={
                    "operation": "merge",
                    "data": {"summary": "{{step_summarize.summary}}"},
                },
                verification_policy=VerificationPolicy.SCHEMA_VALIDATION,
            ),
        ]

    def _sanitize_steps_to_linear(
        self,
        steps: list[WorkflowStepDefinition],
    ) -> list[WorkflowStepDefinition]:
        """Fallback to serialize steps strictly linearly if an AI-generated graph had cycles."""
        sanitized: list[WorkflowStepDefinition] = []
        for i, step in enumerate(steps):
            prev_id = [steps[i - 1].step_id] if i > 0 else []
            sanitized.append(
                WorkflowStepDefinition(
                    step_id=step.step_id,
                    title=step.title,
                    description=step.description,
                    capability_id=step.capability_id,
                    dependencies=prev_id,
                    input_bindings=step.input_bindings,
                    verification_policy=step.verification_policy,
                    timeout_seconds=step.timeout_seconds,
                    max_retries=step.max_retries,
                    requires_authorization=step.requires_authorization,
                    priority=step.priority,
                )
            )
        return sanitized
