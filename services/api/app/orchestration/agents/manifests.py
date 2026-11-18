"""Agent Manifest Catalog and Manifest Validation for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.contracts import (
    AgentCategory,
    AgentContextPolicy,
    AgentExecutionLimits,
    AgentManifest,
    AgentModelProfile,
    AvailabilityState,
)
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.orchestration.agents.manifests")


def validate_manifest(manifest: AgentManifest) -> list[str]:
    """Validate an AgentManifest for integrity, schema validity, and policy conformance.
    
    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []

    if not manifest.agent_id or not manifest.agent_id.replace("_", "").isalnum():
        errors.append(f"Invalid agent_id '{manifest.agent_id}': must be alphanumeric/underscores.")

    if not manifest.name.strip():
        errors.append("Agent name cannot be empty.")

    if not manifest.role.strip():
        errors.append("Agent role cannot be empty.")

    if manifest.execution_limits.concurrency_limit < 1:
        errors.append("Concurrency limit must be at least 1.")

    if manifest.execution_limits.timeout_seconds < 5:
        errors.append("Timeout must be at least 5 seconds.")

    if manifest.model_profile.temperature < 0.0 or manifest.model_profile.temperature > 1.0:
        errors.append("Temperature must be between 0.0 and 1.0.")

    if manifest.context_policy.allow_credentials:
        errors.append("Security violation: specialist agents must not have allow_credentials=True.")

    return errors


def build_default_manifests() -> list[AgentManifest]:
    """Build the definitive catalog of all 24 AUTONOM agents (5 Core + 19 Specialists)."""
    manifests: list[AgentManifest] = [
        # =========================================================================
        # 1. CORE ORCHESTRATION ROLES (Stage 12 Active)
        # =========================================================================
        AgentManifest(
            agent_id="supervisor",
            name="Supervisor Agent",
            role="Workflow Coordinator & Governance Master",
            description="Coordinates multi-agent workflows, lifecycle state transitions, checkpoints, and user governance.",
            category=AgentCategory.ORCHESTRATION,
            version="1.0.0",
            capabilities=["workflow_coordination", "state_management", "checkpoint_preservation"],
            required_permissions=["workflow_control"],
            execution_limits=AgentExecutionLimits(timeout_seconds=300, concurrency_limit=4),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 12 (Active)",
            system_instructions="Coordinate multi-agent execution plans, manage checkpoints, enforce user authorization.",
        ),
        AgentManifest(
            agent_id="planner",
            name="Planning Agent",
            role="Dynamic Workflow Planner",
            description="Decomposes user goals into structured dependency DAGs, enforces cycle detection, and versions plans.",
            category=AgentCategory.ORCHESTRATION,
            version="1.0.0",
            capabilities=["goal_decomposition", "dag_generation", "cycle_detection", "plan_versioning"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=120, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 12 (Active)",
            system_instructions="Decompose goals into deterministic DAGs using Kahn's algorithm for cycle-free dependencies.",
        ),
        AgentManifest(
            agent_id="router",
            name="Task Router Agent",
            role="Capability Dispatcher",
            description="Matches workflow step requirements to capable agents, verifies concurrency and permissions with explainability.",
            category=AgentCategory.ORCHESTRATION,
            version="1.0.0",
            capabilities=["capability_matching", "concurrency_check", "permission_enforcement", "fallback_routing"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=30, concurrency_limit=4),
            model_profile=AgentModelProfile(task_category="fast", local_first=True, temperature=0.0),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 12 (Active)",
            system_instructions="Route steps to qualified agents respecting concurrency limits and hardware guardrails.",
        ),
        AgentManifest(
            agent_id="verifier",
            name="Verification Agent",
            role="Multi-Layer Quality Auditor",
            description="Audits step outputs via deterministic schema/type assertions and semantic model evaluations.",
            category=AgentCategory.ORCHESTRATION,
            version="1.0.0",
            capabilities=["schema_validation", "deterministic_assertion", "semantic_review", "contract_audit"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.0),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 12 (Active)",
            system_instructions="Audit step execution outputs deterministically against JSON schemas and semantic contracts.",
        ),
        AgentManifest(
            agent_id="recovery",
            name="Recovery Agent",
            role="Fault Diagnostician & Healer",
            description="Classifies runtime failures across 13 categories, manages bounded retries, and triggers dynamic replanning.",
            category=AgentCategory.ORCHESTRATION,
            version="1.0.0",
            capabilities=["failure_classification", "bounded_retry", "dynamic_replanning", "state_recovery"],
            required_permissions=["workflow_control"],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 12 (Active)",
            system_instructions="Diagnose errors, select recovery remediations, and prevent infinite retry loops.",
        ),
        AgentManifest(
            agent_id="capability_worker",
            name="Safe Capability Worker",
            role="General Capability Handler",
            description="Executes registered deterministic and AI capabilities safely under hardware guardrails.",
            category=AgentCategory.ORCHESTRATION,
            version="1.0.0",
            capabilities=[
                "text_summarize", "text_classify", "structured_extract",
                "text_compare", "data_transform", "output_validate", "code_inspect"
            ],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=4),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.2),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 12 (Active)",
            system_instructions="Execute discrete capability functions and return validated outputs.",
        ),

        # =========================================================================
        # 2. RECRUITMENT AGENT GROUP (6 Specialist Agents)
        # =========================================================================
        AgentManifest(
            agent_id="job_discovery_agent",
            name="Job Discovery Agent",
            role="Recruitment Opportunity Explorer",
            description="Interprets job search criteria, normalizes user-supplied job listings, and constructs search strategies.",
            category=AgentCategory.RECRUITMENT,
            version="1.0.0",
            capabilities=["recruitment_normalize_job_listing", "recruitment_parse_search_criteria"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.2),
            availability_state=AvailabilityState.LIMITED,
            roadmap_stage="Stage 13 (Limited) / Stages 26-30 (Live Discovery)",
            system_instructions="Extract search criteria and normalize job postings into standard schema. Never claim live board searches without connectors.",
        ),
        AgentManifest(
            agent_id="job_matching_agent",
            name="Job Matching Agent",
            role="Requirement & Skill Match Analyst",
            description="Analyzes job requirements, matches against verified applicant skills, produces explainable alignment scores.",
            category=AgentCategory.RECRUITMENT,
            version="1.0.0",
            capabilities=["recruitment_extract_job_requirements", "recruitment_match_skills"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational)",
            system_instructions="Identify hard/soft skills in jobs and match against verified applicant data. Never invent qualifications.",
        ),
        AgentManifest(
            agent_id="resume_agent",
            name="Resume Agent",
            role="Grounded Resume Tailoring Specialist",
            description="Drafts tailored resume bullet points and section suggestions strictly grounded in verified applicant experience.",
            category=AgentCategory.RECRUITMENT,
            version="1.0.0",
            capabilities=["recruitment_draft_resume_bullets"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="writing", local_first=True, temperature=0.3),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 23 (Full Document)",
            system_instructions="Draft resume achievements highlighting verified skills for the target role. Strictly prohibit fabricating facts.",
        ),
        AgentManifest(
            agent_id="application_agent",
            name="Application Agent",
            role="Application Form & Question Specialist",
            description="Analyzes application question requirements, classifies input fields, drafts evidence-backed responses.",
            category=AgentCategory.RECRUITMENT,
            version="1.0.0",
            capabilities=["recruitment_classify_application_fields"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.2),
            availability_state=AvailabilityState.LIMITED,
            roadmap_stage="Stage 13 (Limited) / Stages 31-35 (Browser Submission)",
            system_instructions="Classify form fields and map to verified profile data. Do not execute browser submissions.",
        ),
        AgentManifest(
            agent_id="recruitment_comms_agent",
            name="Recruitment Communications Agent",
            role="Recruiter Interaction & Correspondence Specialist",
            description="Summarizes recruiter conversations, extracts commitments/dates, and drafts professional communication replies.",
            category=AgentCategory.RECRUITMENT,
            version="1.0.0",
            capabilities=["recruitment_summarize_conversation", "recruitment_draft_recruiter_reply"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="writing", local_first=True, temperature=0.3),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 36 (Email Sync)",
            system_instructions="Summarize recruiter interactions and draft polite professional responses. Do not send live emails.",
        ),
        AgentManifest(
            agent_id="interview_prep_agent",
            name="Interview Preparation Agent",
            role="Technical & Behavioral Interview Coach",
            description="Generates tailored interview questions, scenario drills, and technical review plans based on job requirements.",
            category=AgentCategory.RECRUITMENT,
            version="1.0.0",
            capabilities=["recruitment_generate_interview_questions"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.3),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational)",
            system_instructions="Generate targeted technical and behavioral interview questions mapped to required skills.",
        ),

        # =========================================================================
        # 3. COMPUTER CONTROL AGENT GROUP (4 Specialist Agents)
        # =========================================================================
        AgentManifest(
            agent_id="browser_agent",
            name="Browser Agent",
            role="Autonomous Web Navigation Specialist",
            description="Executes production-oriented browser automation, DOM inspection, safe form filling, and downloads using Playwright.",
            category=AgentCategory.COMPUTER,
            version="1.0.0",
            capabilities=[
                "browser_plan_navigation",
                "browser_navigate",
                "browser_inspect_dom",
                "browser_click",
                "browser_fill",
                "browser_download",
                "browser_submit_form",
                "browser_take_screenshot",
                "browser_manage_tabs",
            ],
            required_permissions=["browser:navigate", "browser:inspect", "browser:interact"],
            execution_limits=AgentExecutionLimits(timeout_seconds=120, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 16",
            system_instructions="Operate Playwright browser automation with fail-closed origin validation, structured DOM inspection, and Stage 14 submission approval.",
        ),
        AgentManifest(
            agent_id="windows_computer_agent",
            name="Windows Computer Agent",
            role="Desktop OS Automation Specialist",
            description="Coordinates native Windows application control, top-level window management, process discovery, and safe desktop action execution.",
            category=AgentCategory.COMPUTER,
            version="1.0.0",
            capabilities=[
                "desktop_plan_operation",
                "desktop_list_applications",
                "desktop_list_windows",
                "desktop_inspect_window",
                "desktop_manage_window",
                "desktop_execute_action",
            ],
            required_permissions=["desktop:window_manage", "desktop:interact", "desktop:launch"],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 17 (Operational)",
            system_instructions="Coordinate native Windows desktop tasks, manage window states, and execute authorized desktop operations through Microsoft UI Automation.",
        ),
        AgentManifest(
            agent_id="visual_grounding_agent",
            name="Visual Grounding Agent",
            role="Screenshot & Visual UI Analyst",
            description="Performs live desktop capture, offline WinRT OCR, visual UI grounding, coordinate transformation, and verified Windows desktop input control.",
            category=AgentCategory.COMPUTER,
            version="1.0.0",
            capabilities=[
                "visual_inspect_image_metadata",
                "visual_capture_display",
                "visual_capture_window",
                "visual_run_ocr",
                "visual_find_text",
                "visual_detect_elements",
                "visual_ground",
                "visual_execute_action",
                "visual_click",
                "visual_enter_text",
            ],
            required_permissions=["desktop:inspect", "desktop:interact"],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=1),
            model_profile=AgentModelProfile(task_category="vision", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 18 (Operational)",
            system_instructions="Capture desktop frames, perform offline OCR, ground interactive elements to desktop coordinates, and execute verified SendInput interactions safely.",
        ),
        AgentManifest(
            agent_id="structural_ui_agent",
            name="Structural UI Agent",
            role="UI Automation Tree Inspector",
            description="Inspects Microsoft UI Automation trees, resolves semantic control locators, and executes standard control patterns (Invoke, Value, Toggle, Select, Scroll).",
            category=AgentCategory.COMPUTER,
            version="1.0.0",
            capabilities=[
                "structural_parse_accessibility_tree",
                "desktop_inspect_tree",
                "desktop_find_elements",
                "desktop_invoke",
                "desktop_set_value",
            ],
            required_permissions=["desktop:inspect", "desktop:interact"],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.0),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 17 (Operational)",
            system_instructions="Traverse live Windows UI Automation trees, resolve accessible controls via semantic locators, and invoke control patterns safely.",
        ),

        # =========================================================================
        # 4. CODING AGENT (1 Specialist Agent)
        # =========================================================================
        AgentManifest(
            agent_id="coding_agent",
            name="Coding Agent",
            role="Software Engineering & Static Analysis Specialist",
            description="Performs code explanation, static code review, bug identification, and test-case generation.",
            category=AgentCategory.DEVELOPMENT,
            version="1.0.0",
            capabilities=["code_explain", "code_review_static", "code_generate_tests", "code_inspect"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="coding", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 41 (Autonomous Repo Editing)",
            system_instructions="Analyze code, explain architecture, review bugs, and suggest unit tests. Do not execute code without authorization.",
        ),

        # =========================================================================
        # 5. RESEARCH AGENT (1 Specialist Agent)
        # =========================================================================
        AgentManifest(
            agent_id="research_agent",
            name="Research Agent",
            role="Information Synthesis & Evidence Verification Specialist",
            description="Synthesizes supplied reference documents, extracts grounded evidence, and compares source consensus.",
            category=AgentCategory.RESEARCH,
            version="1.0.0",
            capabilities=["research_summarize_sources", "research_extract_evidence", "research_compare_sources"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.2),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 44 (Live Web Research)",
            system_instructions="Analyze and compare supplied source documents. Strictly distinguish supplied citations from model reasoning.",
        ),

        # =========================================================================
        # 6. PRODUCTIVITY AGENT GROUP (3 Specialist Agents)
        # =========================================================================
        AgentManifest(
            agent_id="document_agent",
            name="Document Agent",
            role="Structured Technical Writing Specialist",
            description="Drafts structured documents, produces section outlines, and rewrites text for clarity and impact.",
            category=AgentCategory.PRODUCTIVITY,
            version="1.0.0",
            capabilities=["doc_generate_outline", "doc_draft_report", "doc_rewrite_text"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=90, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="writing", local_first=True, temperature=0.3),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 42 (File Generation)",
            system_instructions="Produce well-structured written documents, outlines, and summaries following specified formatting.",
        ),
        AgentManifest(
            agent_id="spreadsheet_agent",
            name="Spreadsheet Agent",
            role="Tabular Data & Formula Analysis Specialist",
            description="Analyzes tabular schemas, computes summary statistics deterministically, and explains spreadsheet formulas.",
            category=AgentCategory.PRODUCTIVITY,
            version="1.0.0",
            capabilities=["sheet_summarize_tabular", "sheet_explain_formula"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 42 (Excel Automation)",
            system_instructions="Compute deterministic summary metrics for tabular data and explain spreadsheet formula logic.",
        ),
        AgentManifest(
            agent_id="presentation_agent",
            name="Presentation Agent",
            role="Slide Deck Narrative & Visual Concept Specialist",
            description="Designs structured slide deck narratives, section structures, and drafts conversational speaker notes.",
            category=AgentCategory.PRODUCTIVITY,
            version="1.0.0",
            capabilities=["pres_generate_outline", "pres_draft_speaker_notes"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="writing", local_first=True, temperature=0.3),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 42 (PowerPoint Export)",
            system_instructions="Create cohesive presentation slide narratives with speaker notes. Do not claim PPTX file export.",
        ),

        # =========================================================================
        # 7. CREATIVE AGENT (1 Specialist Agent)
        # =========================================================================
        AgentManifest(
            agent_id="creative_agent",
            name="Creative Agent",
            role="3D Scene & Creative Brief Architect",
            description="Transforms creative briefs into structured 3D scene specifications, camera/lighting setups, and render plans.",
            category=AgentCategory.CREATIVE,
            version="1.0.0",
            capabilities=["creative_scene_specification"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=1),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.4),
            availability_state=AvailabilityState.LIMITED,
            roadmap_stage="Stage 13 (Limited) / Stage 43 (Blender Automation)",
            system_instructions="Draft structured 3D scene specifications. Do not execute live 3D rendering or Blender control.",
        ),

        # =========================================================================
        # 8. COMMUNICATION AGENT (1 Specialist Agent)
        # =========================================================================
        AgentManifest(
            agent_id="messaging_agent",
            name="Messaging Agent",
            role="Conversational Intelligence & Triage Specialist",
            description="Classifies incoming communications by intent and urgency, and drafts contextual response suggestions.",
            category=AgentCategory.COMMUNICATION,
            version="1.0.0",
            capabilities=["msg_classify_message", "msg_draft_response"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.2),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stages 36-40 (External Service Sync)",
            system_instructions="Classify incoming messages and draft respectful replies. Do not send external messages.",
        ),

        # =========================================================================
        # 9. MARKET INTELLIGENCE AGENT (1 Specialist Agent)
        # =========================================================================
        AgentManifest(
            agent_id="market_intelligence_agent",
            name="Market Intelligence Agent",
            role="Market Data & Competitor Analysis Specialist",
            description="Analyzes supplied market indicators, benchmarks companies, and computes numerical comparisons from evidence.",
            category=AgentCategory.RESEARCH,
            version="1.0.0",
            capabilities=["market_analyze_supplied_data"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=1),
            model_profile=AgentModelProfile(task_category="general", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.LIMITED,
            roadmap_stage="Stage 13 (Limited) / Stage 44 (Live Feeds)",
            system_instructions="Analyze supplied market datasets. Never fabricate live stock quotes or market projections.",
        ),

        # =========================================================================
        # 10. WORKFLOW AUTOMATION AGENT (1 Specialist Agent)
        # =========================================================================
        AgentManifest(
            agent_id="workflow_automation_agent",
            name="Workflow Automation Agent",
            role="Autonomous Pipeline & DAG Configuration Architect",
            description="Decomposes complex automation goals into reusable DAG templates and validates pipeline dependency configurations.",
            category=AgentCategory.AUTOMATION,
            version="1.0.0",
            capabilities=["workflow_propose_template", "workflow_validate_config"],
            required_permissions=[],
            execution_limits=AgentExecutionLimits(timeout_seconds=60, concurrency_limit=2),
            model_profile=AgentModelProfile(task_category="reasoning", local_first=True, temperature=0.1),
            availability_state=AvailabilityState.OPERATIONAL,
            roadmap_stage="Stage 13 (Operational) / Stage 45 (MCP Workflows)",
            system_instructions="Structure automation pipelines into valid DAGs conforming to Stage 12 orchestration schemas.",
        ),
    ]

    return manifests
