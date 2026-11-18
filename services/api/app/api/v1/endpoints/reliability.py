"""Stage 20: Authenticated REST API endpoints for Workflow Reliability, Action Recording, and Recovery."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.computer.workflow_reliability.contracts import (
    CompileProcedureRequest,
    ExecutionCheckpoint,
    PreflightReport,
    ProcedureExecution,
    RecordedAction,
    RecordingSession,
    RecoveryPlan,
    ReliabilityDiagnosticsInfo,
    ReplayMode,
    ReusableProcedure,
    StartRecordingRequest,
)
from app.computer.workflow_reliability.errors import (
    ProcedureNotFoundError,
    ProcedureValidationError,
    RecordingActiveError,
    RecordingClosedError,
    ReplayPreflightFailedError,
    UnrecoverableExecutionError,
    WorkflowReliabilityError,
)
from app.computer.workflow_reliability.service import (
    WorkflowReliabilityService,
    get_workflow_reliability_service,
)
from app.core.security import AuthContext, require_auth

router = APIRouter(prefix="/reliability", tags=["Workflow Reliability"], dependencies=[Depends(require_auth)])


# =============================================================================
# Action Recording Endpoints
# =============================================================================

@router.post(
    "/recordings",
    response_model=RecordingSession,
    status_code=status.HTTP_201_CREATED,
    summary="Start an authorized action recording session",
)
def start_recording(
    req: StartRecordingRequest,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecordingSession:
    try:
        req.agent_id = req.agent_id or auth.client_id
        return service.start_recording(req)
    except RecordingActiveError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/recordings",
    response_model=List[RecordingSession],
    summary="List all recording sessions",
)
def list_recordings(
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> List[RecordingSession]:
    return service.list_sessions()


@router.get(
    "/recordings/{session_id}",
    response_model=RecordingSession,
    summary="Get details of a specific recording session",
)
def get_recording(
    session_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecordingSession:
    sess = service.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recording session '{session_id}' not found.")
    return sess


@router.post(
    "/recordings/{session_id}/pause",
    response_model=RecordingSession,
    summary="Pause an active recording session",
)
def pause_recording(
    session_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecordingSession:
    try:
        return service.pause_recording(session_id)
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/recordings/{session_id}/resume",
    response_model=RecordingSession,
    summary="Resume a paused recording session",
)
def resume_recording(
    session_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecordingSession:
    try:
        return service.resume_recording(session_id)
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/recordings/{session_id}/stop",
    response_model=RecordingSession,
    summary="Stop, seal, and finalize a recording session",
)
def stop_recording(
    session_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecordingSession:
    try:
        return service.stop_recording(session_id)
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


class RecordActionRequest(BaseModel):
    source_adapter: str = "desktop"
    action_type: str = "click"
    target_summary: str = "target"
    target_identity: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    raw_parameters: Optional[Dict[str, Any]] = None
    application_name: Optional[str] = None


@router.post(
    "/recordings/{session_id}/actions",
    response_model=RecordedAction,
    status_code=status.HTTP_201_CREATED,
    summary="Record an action into an active session",
)
def record_action(
    session_id: str,
    req: RecordActionRequest,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecordedAction:
    try:
        t_id = dict(req.target_identity)
        if req.application_name and "process_name" not in t_id:
            t_id["process_name"] = req.application_name
        params = req.parameters if req.parameters else (req.raw_parameters or {})
        act = service.record_action(
            source_adapter=req.source_adapter,
            action_type=req.action_type,
            target_summary=req.target_summary,
            target_identity=t_id,
            parameters=params,
            session_id=session_id,
            agent_id=auth.client_id,
        )
        if not act:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action excluded by recording scope or session not active.")
        return act
    except RecordingClosedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/recordings/{session_id}/actions",
    response_model=List[RecordedAction],
    summary="Get recorded actions for a session",
)
def get_recording_actions(
    session_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> List[RecordedAction]:
    return service.get_session_actions(session_id)


# =============================================================================
# Procedure Endpoints
# =============================================================================

@router.post(
    "/procedures/compile",
    response_model=ReusableProcedure,
    status_code=status.HTTP_201_CREATED,
    summary="Compile a finalized recording into a reusable procedure",
)
def compile_procedure(
    req: CompileProcedureRequest,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ReusableProcedure:
    try:
        return service.compile_procedure(req)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/procedures",
    response_model=List[ReusableProcedure],
    summary="List all registered procedures",
)
def list_procedures(
    category: Optional[str] = Query(None, description="Filter by category"),
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> List[ReusableProcedure]:
    return service.list_procedures(category)


@router.get(
    "/procedures/{procedure_id}",
    response_model=ReusableProcedure,
    summary="Get a specific procedure definition",
)
def get_procedure(
    procedure_id: str,
    version: Optional[int] = Query(None, description="Specific version number"),
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ReusableProcedure:
    proc = service.get_procedure(procedure_id, version)
    if not proc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Procedure '{procedure_id}' not found.")
    return proc


@router.post(
    "/procedures/{procedure_id}/publish",
    response_model=ReusableProcedure,
    summary="Publish a validated procedure version",
)
def publish_procedure(
    procedure_id: str,
    version: int = Query(..., description="Version to publish"),
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ReusableProcedure:
    try:
        return service.publish_procedure(procedure_id, version)
    except ProcedureNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/procedures/{procedure_id}/preflight",
    response_model=PreflightReport,
    summary="Run preflight checks for procedure replay",
)
def run_preflight(
    procedure_id: str,
    arguments: Dict[str, Any],
    version: Optional[int] = None,
    mode: str = "automatic_authorized",
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> PreflightReport:
    try:
        rmode = ReplayMode(mode) if mode in [m.value for m in ReplayMode] else ReplayMode.AUTOMATIC_AUTHORIZED
        return service.run_preflight(procedure_id, arguments, version=version, mode=rmode)
    except ProcedureNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/procedures/{procedure_id}/execute",
    response_model=ProcedureExecution,
    summary="Execute or replay a reusable procedure",
)
async def execute_procedure(
    procedure_id: str,
    arguments: Dict[str, Any],
    version: Optional[int] = None,
    mode: str = "automatic_authorized",
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ProcedureExecution:
    try:
        rmode = ReplayMode(mode) if mode in [m.value for m in ReplayMode] else ReplayMode.AUTOMATIC_AUTHORIZED
        return await service.execute_procedure(procedure_id, arguments, version=version, mode=rmode)
    except ProcedureNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ReplayPreflightFailedError as exc:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc))
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


class ExecuteProcedureApiRequest(BaseModel):
    procedure_id: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    version: Optional[int] = None
    mode: str = "automatic_authorized"


@router.post(
    "/executions",
    response_model=ProcedureExecution,
    status_code=status.HTTP_201_CREATED,
    summary="Execute or replay a reusable procedure",
)
async def create_execution(
    req: ExecuteProcedureApiRequest,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ProcedureExecution:
    try:
        rmode = ReplayMode(req.mode) if req.mode in [m.value for m in ReplayMode] else ReplayMode.AUTOMATIC_AUTHORIZED
        return await service.execute_procedure(req.procedure_id, req.arguments, version=req.version, mode=rmode)
    except ProcedureNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ReplayPreflightFailedError as exc:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(exc))
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# =============================================================================
# Executions & Checkpoints Endpoints
# =============================================================================

@router.get(
    "/executions",
    response_model=List[ProcedureExecution],
    summary="List all procedure executions",
)
def list_executions(
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> List[ProcedureExecution]:
    return service.list_executions()


@router.get(
    "/executions/{execution_id}",
    response_model=ProcedureExecution,
    summary="Get execution details",
)
def get_execution(
    execution_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ProcedureExecution:
    exec_record = service.get_execution(execution_id)
    if not exec_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Execution '{execution_id}' not found.")
    return exec_record


@router.get(
    "/executions/{execution_id}/checkpoints",
    response_model=List[ExecutionCheckpoint],
    summary="List all checkpoints for an execution",
)
def list_checkpoints(
    execution_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> List[ExecutionCheckpoint]:
    return service.list_checkpoints(execution_id)


# =============================================================================
# Recovery Endpoints
# =============================================================================

@router.get(
    "/recovery/pending",
    response_model=List[RecoveryPlan],
    summary="List all executions requiring recovery reconciliation",
)
def list_pending_recoveries(
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> List[RecoveryPlan]:
    return service.reconcile_all_executions()


@router.get(
    "/recovery/{execution_id}",
    response_model=RecoveryPlan,
    summary="Get recovery plan for an interrupted execution",
)
@router.get(
    "/executions/{execution_id}/recovery-plan",
    response_model=RecoveryPlan,
    summary="Get recovery plan for an interrupted execution",
)
def get_recovery_plan(
    execution_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> RecoveryPlan:
    plan = service.get_recovery_plan(execution_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No recovery plan available for '{execution_id}'.")
    return plan


@router.post(
    "/recovery/{execution_id}/resume",
    response_model=ProcedureExecution,
    summary="Resume execution from latest checkpoint",
)
@router.post(
    "/executions/{execution_id}/resume",
    response_model=ProcedureExecution,
    summary="Resume execution from latest checkpoint",
)
async def resume_execution(
    execution_id: str,
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ProcedureExecution:
    try:
        return await service.resume_execution(execution_id)
    except UnrecoverableExecutionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except WorkflowReliabilityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# =============================================================================
# System Diagnostics & Health
# =============================================================================

@router.get(
    "/diagnostics",
    response_model=ReliabilityDiagnosticsInfo,
    summary="Get reliability engine diagnostics and counters",
)
def get_diagnostics(
    service: WorkflowReliabilityService = Depends(get_workflow_reliability_service),
    auth: AuthContext = Depends(require_auth),
) -> ReliabilityDiagnosticsInfo:
    return service.get_diagnostics()
