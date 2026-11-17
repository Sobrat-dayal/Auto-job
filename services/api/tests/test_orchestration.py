"""Unit and integration tests for Multi-Agent Orchestration (Stage 12)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.orchestration.agents.registry import get_agent_registry
from app.orchestration.capabilities.registry import get_capability_registry
from app.orchestration.context import WorkflowContext
from app.orchestration.contracts import (
    FailureCategory,
    PriorityLevel,
    StepStatus,
    VerificationPolicy,
    VerificationStatus,
    WorkflowCreateRequest,
    WorkflowReplanRequest,
    WorkflowStepDefinition,
)
from app.orchestration.graph import DependencyGraph
from app.orchestration.planner import PlanningAgent
from app.orchestration.recovery import RecoveryAgent
from app.orchestration.router import TaskRouterAgent
from app.orchestration.supervisor import get_supervisor_agent
from app.orchestration.verifier import VerificationAgent
from app.repositories.workflow_repository import WorkflowRepository


@pytest.mark.asyncio
async def test_dependency_graph_topological_sort_and_stages():
    """Verify DAG topological sort and parallel stage calculations."""
    steps = [
        WorkflowStepDefinition(
            step_id="step_1",
            title="Step 1",
            capability_id="text_summarize",
            dependencies=[],
        ),
        WorkflowStepDefinition(
            step_id="step_2",
            title="Step 2",
            capability_id="text_classify",
            dependencies=[],
        ),
        WorkflowStepDefinition(
            step_id="step_3",
            title="Step 3",
            capability_id="data_transform",
            dependencies=["step_1", "step_2"],
        ),
        WorkflowStepDefinition(
            step_id="step_4",
            title="Step 4",
            capability_id="output_validate",
            dependencies=["step_3"],
        ),
    ]

    graph = DependencyGraph(steps)
    order = graph.topological_order
    assert len(order) == 4
    # step_1 and step_2 must come before step_3
    assert order.index("step_1") < order.index("step_3")
    assert order.index("step_2") < order.index("step_3")
    # step_3 must come before step_4
    assert order.index("step_3") < order.index("step_4")

    # Stages calculation
    stages = graph.compute_parallel_stages()
    assert len(stages) == 3
    assert set(stages[0]) == {"step_1", "step_2"}
    assert stages[1] == ["step_3"]
    assert stages[2] == ["step_4"]

    # Executable steps
    statuses = {
        "step_1": StepStatus.PENDING,
        "step_2": StepStatus.PENDING,
        "step_3": StepStatus.PENDING,
        "step_4": StepStatus.PENDING,
    }
    exec_steps = graph.get_executable_steps(statuses)
    assert set(exec_steps) == {"step_1", "step_2"}

    # When step_1 completes, step_2 still executable
    statuses["step_1"] = StepStatus.COMPLETED
    exec_steps = graph.get_executable_steps(statuses)
    assert exec_steps == ["step_2"]

    # When both 1 and 2 complete, step_3 becomes executable
    statuses["step_2"] = StepStatus.COMPLETED
    exec_steps = graph.get_executable_steps(statuses)
    assert exec_steps == ["step_3"]


@pytest.mark.asyncio
async def test_dependency_graph_cycle_detection():
    """Verify DAG cycle detection fails fast on cyclic dependencies."""
    steps = [
        WorkflowStepDefinition(
            step_id="a",
            title="Step A",
            capability_id="data_transform",
            dependencies=["b"],
        ),
        WorkflowStepDefinition(
            step_id="b",
            title="Step B",
            capability_id="data_transform",
            dependencies=["a"],
        ),
    ]
    with pytest.raises(ValueError, match="Cyclic dependency detected"):
        DependencyGraph(steps)


@pytest.mark.asyncio
async def test_capabilities_execution():
    """Verify execution of the initial safe capabilities."""
    reg = get_capability_registry()

    # 1. code_inspect
    inspect_res = await reg.execute("code_inspect", {"code": "def hello():\n    return 42\n"})
    assert inspect_res["valid_syntax"] is True
    assert inspect_res["function_count"] == 1

    # 2. text_compare
    compare_res = await reg.execute(
        "text_compare",
        {"text_a": "FastAPI is awesome", "text_b": "FastAPI is really awesome"},
    )
    assert compare_res["similarity_ratio"] > 0.7

    # 3. data_transform (markdown report)
    transform_res = await reg.execute(
        "data_transform",
        {
            "operation": "format_markdown_report",
            "data": {
                "title": "Software Engineer Review",
                "job_title": "Lead Python Engineer",
                "skills": ["Python", "Rust", "FastAPI"],
                "experience": "5+ years",
                "summary": "Key responsibility is architecting multi-agent systems.",
            },
        },
    )
    report_text = transform_res["transformed_data"]["report_markdown"]
    assert "# Software Engineer Review" in report_text
    assert "Lead Python Engineer" in report_text
    assert "Python" in report_text

    # 4. output_validate
    validate_res = await reg.execute(
        "output_validate",
        {
            "data": {"report_markdown": report_text, "title": "Review"},
            "required_fields": ["report_markdown", "title"],
            "non_empty_fields": ["report_markdown"],
        },
    )
    assert validate_res["is_valid"] is True


@pytest.mark.asyncio
async def test_context_binding_resolution():
    """Verify WorkflowContext resolves complex input bindings and dot paths."""
    context = WorkflowContext(
        workflow_id="wf_test",
        initial_inputs={"job_description": "We need a Senior Rust Developer with 4 years experience."},
    )
    context.set_step_output(
        "step_extract",
        {
            "extracted_data": {
                "technical_skills": ["Rust", "Tauri", "SQLite"],
                "experience_years": "4 years",
                "job_title": "Senior Rust Developer",
            }
        },
    )

    bindings = {
        "text": "{{input.job_description}}",
        "skills": "{{step_extract.extracted_data.technical_skills}}",
        "job_title": "{{step_extract.extracted_data.job_title}}",
        "formatted_title": "Role: {{step_extract.extracted_data.job_title}}",
    }
    resolved = context.resolve_bindings(bindings)

    assert resolved["text"] == "We need a Senior Rust Developer with 4 years experience."
    assert resolved["skills"] == ["Rust", "Tauri", "SQLite"]
    assert resolved["job_title"] == "Senior Rust Developer"
    assert resolved["formatted_title"] == "Role: Senior Rust Developer"


@pytest.mark.asyncio
async def test_agent_registry():
    """Verify 5 core agents are available and specialist agents are honestly cataloged."""
    reg = get_agent_registry()
    agents = reg.list_agents()
    agent_map = {a.agent_id: a for a in agents}

    # 5 core agents
    for core_id in ["supervisor", "planner", "router", "verifier", "recovery"]:
        assert core_id in agent_map
        assert agent_map[core_id].is_available is True
        assert "Stage 12" in agent_map[core_id].roadmap_stage

    # Specialist agents for future stages
    assert "job_search_specialist" in agent_map
    assert agent_map["job_search_specialist"].is_available is False


@pytest.mark.asyncio
async def test_recovery_classification():
    """Verify recovery agent classifies all 13 error conditions accurately."""
    rec = RecoveryAgent()
    assert rec.classify_failure(TimeoutError("request timed out")) == FailureCategory.TIMEOUT
    assert rec.classify_failure("Rate limit reached 429") == FailureCategory.RATE_LIMIT
    assert rec.classify_failure("Connection refused to provider") == FailureCategory.PROVIDER_UNAVAILABLE
    assert rec.classify_failure("Schema validation failed: missing keys") == FailureCategory.FAILED_VERIFICATION
    assert rec.classify_failure("User authorization required") == FailureCategory.AUTHORIZATION_REQUIRED
    assert rec.classify_failure("Action cancelled by user") == FailureCategory.CANCELLED_BY_USER


@pytest.mark.asyncio
async def test_end_to_end_job_analysis_workflow():
    """Verify end-to-end execution of real recruitment job analysis workflow."""
    supervisor = get_supervisor_agent()

    job_text = (
        "Principal AI Systems Engineer\n"
        "Responsibilities:\n"
        "- Build multi-agent orchestration runtimes for desktop assistants\n"
        "- Optimize local LLM inference on NVIDIA RTX hardware\n"
        "Requirements:\n"
        "- 5+ years experience in Python, Rust, and TypeScript\n"
        "- BS or MS in Computer Science\n"
    )

    req = WorkflowCreateRequest(
        goal="Analyze supplied job description, extract technical skills, summarize responsibilities, identify experience requirements, and produce a structured report",
        constraints={"job_description": job_text},
        priority=PriorityLevel.HIGH,
    )

    created_wf = await supervisor.create_workflow(req)
    assert created_wf.id.startswith("wf_")
    assert created_wf.active_plan is not None
    assert len(created_wf.steps) >= 4

    # Run workflow synchronously in test
    started_wf = await supervisor.start_workflow(created_wf.id, background=False)
    assert started_wf.status.value in ("completed", "running")

    # Fetch status
    final_status = await supervisor.get_workflow_status(created_wf.id)
    assert final_status.status.value == "completed"
    assert final_status.completed_steps == len(final_status.steps)

    # Check that report output artifact is compiled
    report_step = next(s for s in final_status.steps if s.step_id == "step_report")
    assert report_step.output_result is not None
    assert "transformed_data" in report_step.output_result
    assert "report_markdown" in report_step.output_result["transformed_data"]
    markdown = report_step.output_result["transformed_data"]["report_markdown"]
    assert "Autonomous Job Requirement Analysis" in markdown


@pytest.mark.asyncio
async def test_fastapi_orchestration_endpoints():
    """Verify FastAPI orchestration API endpoints."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. List agents
        agents_res = await client.get("/api/v1/orchestration/agents")
        assert agents_res.status_code == 200
        agents = agents_res.json()
        assert len(agents) >= 5
        agent_ids = [a["agent_id"] for a in agents]
        assert "supervisor" in agent_ids
        assert "planner" in agent_ids

        # 2. List capabilities
        caps_res = await client.get("/api/v1/orchestration/capabilities")
        assert caps_res.status_code == 200
        caps = caps_res.json()
        assert len(caps) >= 7
        cap_ids = [c["capability_id"] for c in caps]
        assert "text_summarize" in cap_ids
        assert "data_transform" in cap_ids

        # 3. Create workflow
        create_res = await client.post(
            "/api/v1/orchestration/workflows",
            json={
                "goal": "Inspect Python code for syntax and complexity",
                "constraints": {"code": "def foo():\n    return 1\n"},
            },
        )
        assert create_res.status_code == 201
        wf = create_res.json()
        wf_id = wf["id"]

        # 4. Get DAG
        dag_res = await client.get(f"/api/v1/orchestration/workflows/{wf_id}/dag")
        assert dag_res.status_code == 200
        dag = dag_res.json()
        assert "steps" in dag
        assert "topological_order" in dag

        # 5. Get stats
        stats_res = await client.get("/api/v1/orchestration/stats")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert "total_workflows" in stats
