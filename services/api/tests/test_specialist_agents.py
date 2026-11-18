"""Comprehensive test suite for Specialist AI Agent Framework, Multi-Agent Collaboration, and APIs (Stage 13)."""

from datetime import UTC, datetime
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.orchestration.agents.contracts import (
    AgentCategory,
    AgentConfigurationUpdate,
    AgentContextPolicy,
    AgentExecutionLimits,
    AgentManifest,
    AgentModelProfile,
    AvailabilityState,
)
from app.orchestration.agents.manifests import validate_manifest
from app.orchestration.agents.registry import get_agent_registry
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.contracts import (
    PriorityLevel,
    StepStatus,
    WorkflowCreateRequest,
    WorkflowStatus,
)
from app.orchestration.supervisor import get_supervisor_agent


@pytest.mark.asyncio
async def test_agent_manifest_validation():
    """Verify AgentManifest integrity checks, schema validation, and security policies."""
    # Valid manifest
    valid = AgentManifest(
        agent_id="test_specialist",
        name="Test Specialist",
        role="Unit Tester",
        description="Test agent description",
        category=AgentCategory.DEVELOPMENT,
    )
    errors = validate_manifest(valid)
    assert len(errors) == 0

    # Invalid agent_id
    invalid_id = AgentManifest(
        agent_id="invalid id with spaces!",
        name="Bad Agent",
        role="Role",
        description="Desc",
        category=AgentCategory.AUTOMATION,
    )
    errors = validate_manifest(invalid_id)
    assert any("Invalid agent_id" in e for e in errors)

    # Security rule: context policy credentials prohibited
    unsafe_manifest = AgentManifest(
        agent_id="unsafe_agent",
        name="Unsafe Agent",
        role="Leaker",
        description="Desc",
        category=AgentCategory.RECRUITMENT,
        context_policy=AgentContextPolicy(allow_credentials=True),
    )
    errors = validate_manifest(unsafe_manifest)
    assert any("allow_credentials" in e for e in errors)


@pytest.mark.asyncio
async def test_agent_catalog_registration():
    """Verify that all 24 agents (5 core + 19 specialists) are registered with honest availability."""
    reg = get_agent_registry()
    manifests = reg.list_manifests()
    manifest_map = {m.agent_id: m for m in manifests}

    assert len(manifests) >= 24

    # 5 Core Orchestration Agents
    for cid in ["supervisor", "planner", "router", "verifier", "recovery"]:
        assert cid in manifest_map
        assert manifest_map[cid].category == AgentCategory.ORCHESTRATION
        assert manifest_map[cid].availability_state == AvailabilityState.OPERATIONAL

    # 6 Recruitment Specialist Roles
    recruitment_roles = [
        ("job_discovery_agent", AvailabilityState.LIMITED),
        ("job_matching_agent", AvailabilityState.OPERATIONAL),
        ("resume_agent", AvailabilityState.OPERATIONAL),
        ("application_agent", AvailabilityState.LIMITED),
        ("recruitment_comms_agent", AvailabilityState.OPERATIONAL),
        ("interview_prep_agent", AvailabilityState.OPERATIONAL),
    ]
    for aid, state in recruitment_roles:
        assert aid in manifest_map
        assert manifest_map[aid].category == AgentCategory.RECRUITMENT
        assert manifest_map[aid].availability_state == state

    # 4 Computer Control Roles
    computer_roles = [
        ("browser_agent", AvailabilityState.OPERATIONAL),
        ("windows_computer_agent", AvailabilityState.OPERATIONAL),
        ("visual_grounding_agent", AvailabilityState.LIMITED),
        ("structural_ui_agent", AvailabilityState.OPERATIONAL),
    ]
    for aid, state in computer_roles:
        assert aid in manifest_map
        assert manifest_map[aid].category == AgentCategory.COMPUTER
        assert manifest_map[aid].availability_state == state

    # Other Specialists
    assert manifest_map["coding_agent"].category == AgentCategory.DEVELOPMENT
    assert manifest_map["coding_agent"].availability_state == AvailabilityState.OPERATIONAL

    assert manifest_map["research_agent"].category == AgentCategory.RESEARCH
    assert manifest_map["research_agent"].availability_state == AvailabilityState.OPERATIONAL

    assert manifest_map["document_agent"].category == AgentCategory.PRODUCTIVITY
    assert manifest_map["document_agent"].availability_state == AvailabilityState.OPERATIONAL

    assert manifest_map["spreadsheet_agent"].category == AgentCategory.PRODUCTIVITY
    assert manifest_map["spreadsheet_agent"].availability_state == AvailabilityState.OPERATIONAL

    assert manifest_map["presentation_agent"].category == AgentCategory.PRODUCTIVITY
    assert manifest_map["presentation_agent"].availability_state == AvailabilityState.OPERATIONAL

    assert manifest_map["creative_agent"].category == AgentCategory.CREATIVE
    assert manifest_map["creative_agent"].availability_state == AvailabilityState.LIMITED

    assert manifest_map["messaging_agent"].category == AgentCategory.COMMUNICATION
    assert manifest_map["messaging_agent"].availability_state == AvailabilityState.OPERATIONAL

    assert manifest_map["market_intelligence_agent"].category == AgentCategory.RESEARCH
    assert manifest_map["market_intelligence_agent"].availability_state == AvailabilityState.LIMITED

    assert manifest_map["workflow_automation_agent"].category == AgentCategory.AUTOMATION
    assert manifest_map["workflow_automation_agent"].availability_state == AvailabilityState.OPERATIONAL


@pytest.mark.asyncio
async def test_specialist_capability_execution():
    """Verify execution of discrete safe specialist capabilities."""
    cap_reg = get_capability_registry()

    # 1. Recruitment: Extract Job Requirements
    req_out = await cap_reg.execute(
        "recruitment_extract_job_requirements",
        {
            "job_description": "We are seeking a Senior Python Engineer with 5+ years of experience in FastAPI, Docker, and PostgreSQL.",
            "role_title": "Senior Python Engineer",
        },
    )
    assert len(req_out["required_skills"]) > 0
    assert "Python" in [s.title() for s in req_out["required_skills"]]

    # 2. Recruitment: Match Skills
    match_out = await cap_reg.execute(
        "recruitment_match_skills",
        {
            "required_skills": ["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
            "applicant_skills": ["Python", "FastAPI", "React", "PostgreSQL"],
            "role_title": "Senior Python Engineer",
        },
    )
    assert "Python" in match_out["matched_skills"]
    assert "Kubernetes" in match_out["missing_skills"]
    assert match_out["match_percentage"] == 75

    # 3. Recruitment: Resume Bullets
    resume_out = await cap_reg.execute(
        "recruitment_draft_resume_bullets",
        {
            "matched_skills": ["Python", "FastAPI"],
            "verified_experience": ["Led development of microservices handling 10k req/sec"],
            "target_role": "Backend Engineer",
        },
    )
    assert len(resume_out["suggested_bullets"]) > 0
    assert resume_out["grounded_in_evidence"] is True

    # 4. Coding: Code Explanation & Review
    code_out = await cap_reg.execute(
        "code_explain",
        {
            "code": "def fib(n: int) -> int:\n    return n if n <= 1 else fib(n-1) + fib(n-2)",
            "language": "python",
        },
    )
    assert code_out["language"] == "python"
    assert "complexity" in code_out

    # 5. Productivity: Spreadsheet Summarize
    sheet_out = await cap_reg.execute(
        "sheet_summarize_tabular",
        {
            "records": [
                {"department": "Engineering", "budget": 100000, "active": True},
                {"department": "Marketing", "budget": 50000, "active": True},
            ],
        },
    )
    assert sheet_out["total_rows"] == 2
    assert sheet_out["numeric_summaries"]["budget"]["sum"] == 150000


@pytest.mark.asyncio
async def test_live_recruitment_multi_agent_workflow():
    """Verify Section 52 Required Live Multi-Agent Workflow Scenario.
    
    Goal: Analyze job description, compare with verified skills, suggest resume bullets,
    create interview prep plan, and synthesize report.
    """
    supervisor = get_supervisor_agent()

    goal = (
        "Analyze this supplied software-engineering job description, identify the required skills, "
        "compare them against my provided verified skills, suggest grounded resume improvements, "
        "and create an interview preparation plan."
    )
    job_desc = (
        "Senior Backend Systems Engineer\n"
        "Requirements:\n"
        "- 4+ years of professional software engineering in Python and FastAPI\n"
        "- Experience with Docker, PostgreSQL, and distributed caching (Redis)\n"
        "- Knowledge of REST APIs, unit testing with pytest, and CI/CD pipelines."
    )
    constraints = {
        "job_description": job_desc,
        "role_title": "Senior Backend Systems Engineer",
        "applicant_skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "Git", "React"],
        "verified_experience": [
            "Built distributed async services processing 50M daily events with 99.99% uptime.",
            "Containerized core microservices using Docker and orchestrated CI/CD pipelines.",
        ],
    }

    # 1. Create Workflow Plan
    req = WorkflowCreateRequest(
        title="Multi-Agent Recruitment Demonstration",
        goal=goal,
        constraints=constraints,
        priority=PriorityLevel.HIGH,
    )
    wf_response = await supervisor.create_workflow(req)
    assert wf_response.status == WorkflowStatus.PLAN_READY
    assert len(wf_response.steps) >= 5

    # 2. Execute Workflow
    completed_wf = await supervisor.start_workflow(wf_response.id, background=False)

    assert completed_wf.status == WorkflowStatus.COMPLETED
    assert completed_wf.completed_steps == len(completed_wf.steps)
    assert completed_wf.failed_steps == 0

    # 3. Verify step outputs and agent routing
    steps_by_cap = {s.capability_id: s for s in completed_wf.steps}

    # Requirements extraction step
    assert "recruitment_extract_job_requirements" in steps_by_cap
    step_extract = steps_by_cap["recruitment_extract_job_requirements"]
    assert step_extract.status == StepStatus.COMPLETED
    assert "Python" in [s.title() for s in step_extract.output_result["required_skills"]]

    # Skill match step
    assert "recruitment_match_skills" in steps_by_cap
    step_match = steps_by_cap["recruitment_match_skills"]
    assert step_match.status == StepStatus.COMPLETED
    assert "Python" in step_match.output_result["matched_skills"]
    assert step_match.output_result["match_percentage"] >= 50

    # Resume bullet drafting step
    assert "recruitment_draft_resume_bullets" in steps_by_cap
    step_resume = steps_by_cap["recruitment_draft_resume_bullets"]
    assert step_resume.status == StepStatus.COMPLETED
    assert len(step_resume.output_result["suggested_bullets"]) > 0

    # Interview prep step
    assert "recruitment_generate_interview_questions" in steps_by_cap
    step_interview = steps_by_cap["recruitment_generate_interview_questions"]
    assert step_interview.status == StepStatus.COMPLETED
    assert len(step_interview.output_result["technical_questions"]) > 0

    # Document synthesis step
    assert "doc_draft_report" in steps_by_cap
    step_report = steps_by_cap["doc_draft_report"]
    assert step_report.status == StepStatus.COMPLETED
    assert step_report.output_result["word_count"] > 20


@pytest.mark.asyncio
async def test_live_coding_technical_review_workflow():
    """Verify Section 53 Second Live Workflow Test (Coding & Documentation).
    
    Goal: Analyze Python function, identify bugs, suggest improvements, generate test cases,
    and create structured technical review.
    """
    supervisor = get_supervisor_agent()

    goal = (
        "Analyze this supplied Python function, identify possible bugs, "
        "suggest improvements, generate test cases, and create a structured technical review."
    )
    code_sample = (
        "def compute_discount(price: float, discount_percent: float) -> float:\n"
        "    if discount_percent < 0 or discount_percent > 100:\n"
        "        raise ValueError('Invalid discount')\n"
        "    return price * (1.0 - discount_percent / 100.0)\n"
    )
    constraints = {"source_code": code_sample}

    req = WorkflowCreateRequest(
        title="Coding Specialist Technical Review",
        goal=goal,
        constraints=constraints,
        priority=PriorityLevel.INTERACTIVE,
    )
    wf_response = await supervisor.create_workflow(req)
    assert wf_response.status == WorkflowStatus.PLAN_READY

    completed_wf = await supervisor.start_workflow(wf_response.id, background=False)

    assert completed_wf.status == WorkflowStatus.COMPLETED
    assert completed_wf.completed_steps == len(completed_wf.steps)

    steps_by_cap = {s.capability_id: s for s in completed_wf.steps}
    assert "code_explain" in steps_by_cap
    assert "code_review_static" in steps_by_cap
    assert "code_generate_tests" in steps_by_cap
    assert "doc_draft_report" in steps_by_cap

    test_step = steps_by_cap["code_generate_tests"]
    assert "def test_" in test_step.output_result["test_code"]


@pytest.mark.asyncio
async def test_agent_api_endpoints():
    """Verify FastAPI authenticated endpoints for agent directory, status, and config."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. List all agents
        resp = await client.get("/api/v1/agents")
        assert resp.status_code == 200
        agents = resp.json()
        assert len(agents) >= 24

        # 2. Filter by category
        resp_rec = await client.get("/api/v1/agents?category=recruitment")
        assert resp_rec.status_code == 200
        rec_agents = resp_rec.json()
        assert len(rec_agents) == 6

        # 3. Retrieve agent details
        resp_single = await client.get("/api/v1/agents/job_matching_agent")
        assert resp_single.status_code == 200
        assert resp_single.json()["name"] == "Job Matching Agent"

        # 4. List agent capabilities
        resp_caps = await client.get("/api/v1/agents/job_matching_agent/capabilities")
        assert resp_caps.status_code == 200
        cap_ids = [c["capability_id"] for c in resp_caps.json()]
        assert "recruitment_match_skills" in cap_ids

        # 5. Retrieve status
        resp_status = await client.get("/api/v1/agents/job_matching_agent/status")
        assert resp_status.status_code == 200
        assert resp_status.json()["agent_id"] == "job_matching_agent"

        # 6. Retrieve configuration & update
        resp_cfg = await client.get("/api/v1/agents/job_matching_agent/configuration")
        assert resp_cfg.status_code == 200

        patch_resp = await client.patch(
            "/api/v1/agents/job_matching_agent/configuration",
            json={"timeout_seconds": 100, "temperature": 0.25},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["model_profile"]["temperature"] == 0.25

        # 7. Diagnostic test endpoint
        resp_diag = await client.post("/api/v1/agents/job_matching_agent/test")
        assert resp_diag.status_code == 200
        assert resp_diag.json()["passed"] is True

        # 8. All capabilities endpoint
        resp_all_caps = await client.get("/api/v1/agents/capabilities")
        assert resp_all_caps.status_code == 200
        assert len(resp_all_caps.json()) >= 15
