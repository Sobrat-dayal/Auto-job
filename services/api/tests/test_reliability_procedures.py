"""Unit tests for Stage 20 Procedure Compilation, Parameterization, Risk Analysis, and Immutability."""

import pytest
from app.computer.workflow_reliability.contracts import (
    CompileProcedureRequest,
    ProcedureParameter,
    ProcedureStep,
    ProcedureValidationStatus,
    ReusableProcedure,
    SideEffectClass,
    StartRecordingRequest,
)
from app.computer.workflow_reliability.errors import (
    ProcedureNotFoundError,
    ProcedureValidationError,
    ProcedureVersionConflictError,
)
from app.computer.workflow_reliability.procedures.compiler import ProcedureCompiler
from app.computer.workflow_reliability.procedures.registry import ProcedureRegistry
from app.computer.workflow_reliability.procedures.risk_analyzer import ProcedureRiskAnalyzer
from app.computer.workflow_reliability.procedures.validator import ProcedureValidator
from app.computer.workflow_reliability.service import WorkflowReliabilityService


def test_procedure_compilation_and_parameterization():
    service = WorkflowReliabilityService()
    req = StartRecordingRequest(
        name="Compilation Test Recording",
        allowed_app_scopes=["calc.exe"],
    )
    session = service.start_recording(req)
    service.record_action(
        session_id=session.session_id,
        source_adapter="desktop",
        action_type="type_text",
        raw_parameters={"text": "42"},
        application_name="calc.exe",
    )
    service.record_action(
        session_id=session.session_id,
        source_adapter="desktop",
        action_type="click",
        raw_parameters={"target_name": "Equals"},
        application_name="calc.exe",
    )
    stopped = service.stop_recording(session.session_id)

    comp_req = CompileProcedureRequest(
        session_id=stopped.session_id,
        name="Calculator Operation",
        description="Enters 42 and clicks equals",
        parameterize_inputs=True,
    )
    proc = service.compile_procedure(comp_req)
    assert proc.name == "Calculator Operation"
    assert proc.version == 1
    assert len(proc.steps) == 2
    assert len(proc.parameters) >= 1
    assert proc.validation_status == ProcedureValidationStatus.VALID


def test_procedure_validator_blocks_invalid_structures():
    validator = ProcedureValidator()
    # Duplicate step IDs
    invalid_proc = ReusableProcedure(
        procedure_id="proc_invalid",
        version=1,
        name="Invalid Procedure",
        category="general",
        parameters=[ProcedureParameter(name="param1", type="string", required=True)],
        steps=[
            ProcedureStep(
                step_id="step_duplicate",
                order_index=1,
                name="Step 1",
                action_type="click",
                target_surface="desktop",
            ),
            ProcedureStep(
                step_id="step_duplicate",
                order_index=2,
                name="Step 2",
                action_type="click",
                target_surface="desktop",
            ),
        ],
    )
    issues = validator.validate(invalid_proc)
    assert any("Duplicate step_id" in issue for issue in issues)


def test_procedure_registry_versioning_and_immutability():
    registry = ProcedureRegistry()
    proc = ReusableProcedure(
        procedure_id="proc_calc_v1",
        version=1,
        name="Calc v1",
        category="desktop",
        is_draft=True,
        steps=[
            ProcedureStep(
                step_id="s1",
                order_index=1,
                name="Click",
                action_type="click",
                target_surface="desktop",
            )
        ],
    )
    registry.save_draft(proc)
    published = registry.publish_version("proc_calc_v1")
    assert published.is_draft is False

    # Attempting to modify published version directly must raise ProcedureVersionConflictError
    with pytest.raises(ProcedureVersionConflictError):
        registry.save_draft(published)

    # Branching a new draft creates version 2
    draft_v2 = registry.branch_new_draft("proc_calc_v1")
    assert draft_v2.version == 2
    assert draft_v2.is_draft is True
