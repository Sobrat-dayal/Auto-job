"""Stage 20 Workflow Reliability Capabilities for Supervisor and Specialist Agents."""

from typing import Any, Dict, Optional
from app.computer.workflow_reliability.contracts import (
    CompileProcedureRequest,
    ReplayMode,
    StartRecordingRequest,
)
from app.computer.workflow_reliability.service import get_workflow_reliability_service
from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy


class StartRecordingCapability(BaseCapability):
    """Starts an authorized computer action recording session."""

    capability_id = "reliability_start_recording"
    name = "Start Action Recording"
    version = "1.0.0"
    description = "Initiates structured, privacy-filtered computer action recording across browser, native desktop, and visual surfaces."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Session human-readable label"},
                "allowed_app_scopes": {"type": "array", "items": {"type": "string"}},
                "allowed_web_origins": {"type": "array", "items": {"type": "string"}},
            },
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["session_id", "status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        ctx = context or {}
        service = get_workflow_reliability_service()
        req = StartRecordingRequest(
            name=input_data.get("name", "Agent Action Recording"),
            allowed_app_scopes=input_data.get("allowed_app_scopes", []),
            allowed_web_origins=input_data.get("allowed_web_origins", []),
            workflow_id=ctx.get("workflow_id"),
            agent_id=ctx.get("agent_id"),
        )
        session = service.start_recording(req)
        return {"session_id": session.session_id, "status": session.status.value}


class StopRecordingCapability(BaseCapability):
    """Stops, seals, and finalizes an active recording session."""

    capability_id = "reliability_stop_recording"
    name = "Stop Action Recording"
    version = "1.0.0"
    description = "Stops recording, finalizes action sequencing, and computes cryptographic integrity hash."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID to stop"},
            },
            "required": ["session_id"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "status": {"type": "string"},
                "captured_actions": {"type": "integer"},
                "integrity_hash": {"type": "string"},
            },
            "required": ["session_id", "status", "captured_actions", "integrity_hash"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        service = get_workflow_reliability_service()
        session = service.stop_recording(input_data["session_id"])
        return {
            "session_id": session.session_id,
            "status": session.status.value,
            "captured_actions": session.captured_actions_count,
            "integrity_hash": session.integrity_hash,
        }


class CompileProcedureCapability(BaseCapability):
    """Compiles a finalized recording into a reusable parameterized procedure."""

    capability_id = "reliability_compile_procedure"
    name = "Compile Reusable Procedure"
    version = "1.0.0"
    description = "Transforms a recorded action history into a versioned, parameterized, validated ReusableProcedure."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 60
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "parameterize_inputs": {"type": "boolean"},
            },
            "required": ["session_id", "name"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "procedure_id": {"type": "string"},
                "version": {"type": "integer"},
                "name": {"type": "string"},
                "steps_count": {"type": "integer"},
                "parameters_count": {"type": "integer"},
                "validation_status": {"type": "string"},
            },
            "required": ["procedure_id", "version", "name", "steps_count", "parameters_count", "validation_status"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        service = get_workflow_reliability_service()
        req = CompileProcedureRequest(
            session_id=input_data["session_id"],
            name=input_data["name"],
            description=input_data.get("description", ""),
            parameterize_inputs=input_data.get("parameterize_inputs", True),
        )
        proc = service.compile_procedure(req)
        return {
            "procedure_id": proc.procedure_id,
            "version": proc.version,
            "name": proc.name,
            "steps_count": len(proc.steps),
            "parameters_count": len(proc.parameters),
            "validation_status": proc.validation_status.value,
        }


class ExecuteProcedureCapability(BaseCapability):
    """Executes a reusable procedure with preflight verification and checkpoints."""

    capability_id = "reliability_execute_procedure"
    name = "Execute Procedure"
    version = "1.0.0"
    description = "Replays a reusable procedure with state-aware element resolution, authorization checks, and durable checkpoints."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 180
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "procedure_id": {"type": "string"},
                "version": {"type": "integer"},
                "arguments": {"type": "object"},
                "mode": {"type": "string", "enum": ["dry_run", "step_by_step", "automatic_authorized"]},
            },
            "required": ["procedure_id"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "execution_id": {"type": "string"},
                "status": {"type": "string"},
                "completed_steps": {"type": "integer"},
                "execution_time_ms": {"type": "integer"},
                "error_message": {"type": "string"},
            },
            "required": ["execution_id", "status", "completed_steps", "execution_time_ms"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        service = get_workflow_reliability_service()
        mode_str = input_data.get("mode", "automatic_authorized")
        mode = ReplayMode(mode_str) if mode_str in [m.value for m in ReplayMode] else ReplayMode.AUTOMATIC_AUTHORIZED
        execution = await service.execute_procedure(
            procedure_id=input_data["procedure_id"],
            arguments=input_data.get("arguments", {}),
            version=input_data.get("version"),
            mode=mode,
        )
        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "completed_steps": len(execution.completed_steps),
            "execution_time_ms": execution.execution_time_ms,
            "error_message": execution.error_message or "",
        }


class ResumeExecutionCapability(BaseCapability):
    """Resumes an interrupted procedure execution from its latest valid checkpoint."""

    capability_id = "reliability_resume_execution"
    name = "Resume Interrupted Execution"
    version = "1.0.0"
    description = "Reconciles an interrupted execution from durable checkpoints and side-effect records without duplicating work."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds = 180
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "execution_id": {"type": "string"},
            },
            "required": ["execution_id"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "execution_id": {"type": "string"},
                "status": {"type": "string"},
                "completed_steps": {"type": "integer"},
                "execution_time_ms": {"type": "integer"},
            },
            "required": ["execution_id", "status", "completed_steps", "execution_time_ms"],
        }

    async def execute(
        self,
        input_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        service = get_workflow_reliability_service()
        execution = await service.resume_execution(input_data["execution_id"])
        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "completed_steps": len(execution.completed_steps),
            "execution_time_ms": execution.execution_time_ms,
        }
