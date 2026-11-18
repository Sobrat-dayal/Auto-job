"""Unit tests for Stage 20 State-Aware Replay, Preflight Checks, and Execution."""

import pytest
from app.computer.workflow_reliability.contracts import (
    ProcedureExecutionStatus,
    ProcedureParameter,
    ProcedureStep,
    ReplayMode,
    ReusableProcedure,
    SideEffectClass,
)
from app.computer.workflow_reliability.errors import (
    EmergencyStopActiveError,
    ReplayPreflightFailedError,
)
from app.computer.workflow_reliability.replay.preflight import ReplayPreflightEngine
from app.computer.workflow_reliability.service import WorkflowReliabilityService


@pytest.mark.asyncio
async def test_replay_preflight_detects_missing_parameters():
    preflight_engine = ReplayPreflightEngine()
    proc = ReusableProcedure(
        procedure_id="proc_login",
        version=1,
        name="Login Flow",
        category="browser",
        parameters=[
            ProcedureParameter(name="username", type="string", required=True),
            ProcedureParameter(name="password", type="string", required=True, is_secret=True),
        ],
        steps=[
            ProcedureStep(
                step_id="s1",
                order_index=1,
                name="Type Username",
                action_type="fill",
                target_surface="browser",
                input_bindings={"text": "{{username}}"},
            )
        ],
    )
    # Missing both parameters
    report = preflight_engine.run_preflight(proc, {})
    assert report.can_execute is False
    assert "username" in report.missing_parameters
    assert "password" in report.missing_parameters

    # Supplied arguments
    valid_report = preflight_engine.run_preflight(
        proc, {"username": "admin@autonom.ai", "password": "secure_password"}
    )
    assert valid_report.can_execute is True
    assert len(valid_report.missing_parameters) == 0


@pytest.mark.asyncio
async def test_replay_executor_dry_run_and_parameter_interpolation():
    service = WorkflowReliabilityService()
    proc = ReusableProcedure(
        procedure_id="proc_search",
        version=1,
        name="Web Search Procedure",
        category="browser",
        is_draft=False,
        parameters=[
            ProcedureParameter(name="query", type="string", default_value="autonom"),
        ],
        steps=[
            ProcedureStep(
                step_id="step_type_query",
                order_index=1,
                name="Type Search Term",
                action_type="fill",
                target_surface="browser",
                locator_schema={"selector": "input[name='q']"},
                input_bindings={"text": "{{query}}"},
                side_effect_class=SideEffectClass.READ_ONLY,
            ),
            ProcedureStep(
                step_id="step_click_search",
                order_index=2,
                name="Click Search Button",
                action_type="click",
                target_surface="browser",
                locator_schema={"selector": "button#submit"},
                input_bindings={},
                side_effect_class=SideEffectClass.IDEMPOTENT,
            ),
        ],
    )
    service.procedure_registry.save_draft(proc)
    service.procedure_registry.publish_version(proc.procedure_id)

    # Dry run execution
    execution = await service.execute_procedure(
        procedure_id=proc.procedure_id,
        arguments={"query": "Windows Automation"},
        mode=ReplayMode.DRY_RUN,
    )
    assert execution.status == ProcedureExecutionStatus.COMPLETED
    assert len(execution.completed_steps) == 2
    assert execution.resolved_arguments["query"] == "Windows Automation"
    assert len(execution.checkpoints) >= 1
