"""Procedure compiler transforming recorded actions into declarative ReusableProcedure definitions."""

from typing import List, Optional
import uuid

from app.computer.workflow_reliability.contracts import (
    CheckpointPolicy,
    CompileProcedureRequest,
    ProcedureParameter,
    ProcedureStep,
    ProcedureValidationStatus,
    RecordedAction,
    RecordingSession,
    ReusableProcedure,
    SideEffectClass,
)
from app.computer.workflow_reliability.errors import ProcedureCompilationError
from app.computer.workflow_reliability.procedures.risk_analyzer import ProcedureRiskAnalyzer
from app.computer.workflow_reliability.procedures.validator import ProcedureValidator


class ProcedureCompiler:
    """Compiles normalized RecordedAction sequences into parameterized ReusableProcedure contracts."""

    @classmethod
    def compile_from_recording(
        cls,
        session: RecordingSession,
        actions: List[RecordedAction],
        req: CompileProcedureRequest,
    ) -> ReusableProcedure:
        """Transform recorded action history into a versioned ReusableProcedure."""
        if not actions:
            raise ProcedureCompilationError(f"Cannot compile procedure: Recording session '{session.session_id}' contains no actions.")

        steps: List[ProcedureStep] = []
        parameters: List[ProcedureParameter] = []
        param_counter = 1

        for idx, act in enumerate(actions):
            # Clean transient process/window IDs from target definition
            cleaned_target = dict(act.target_identity)
            cleaned_target.pop("process_id", None)
            cleaned_target.pop("window_handle", None)

            input_bindings = dict(act.approved_parameters)

            # Auto-parameterize input text if requested
            if req.parameterize_inputs:
                for param_key in ("input_text", "text", "value"):
                    if param_key in input_bindings and isinstance(input_bindings[param_key], str):
                        raw_val = input_bindings[param_key]
                        if raw_val and not raw_val.startswith("[REDACTED"):
                            param_name = f"input_text_{param_counter}"
                            param_counter += 1
                            parameters.append(
                                ProcedureParameter(
                                    name=param_name,
                                    type="string",
                                    required=True,
                                    default_value=raw_val,
                                    description=f"Input text for step {idx + 1} ({act.target_summary})",
                                )
                            )
                            input_bindings[param_key] = f"{{{{{param_name}}}}}"

            # Classify side effect and checkpoint policies
            act_type_lower = act.action_type.lower()
            if act_type_lower in ("submit", "email", "payment", "delete"):
                side_effect = SideEffectClass.NON_IDEMPOTENT
                checkpoint_policy = CheckpointPolicy.BEFORE_IRREVERSIBLE
            elif act_type_lower in ("navigate", "inspect"):
                side_effect = SideEffectClass.READ_ONLY
                checkpoint_policy = CheckpointPolicy.NONE
            else:
                side_effect = SideEffectClass.IDEMPOTENT
                checkpoint_policy = CheckpointPolicy.STEP if idx % 5 == 0 else CheckpointPolicy.NONE

            step = ProcedureStep(
                step_id=f"step_{idx + 1}_{act.action_type}",
                sequence_index=idx,
                capability_id=act.capability_id,
                preferred_method=act.source_adapter,
                target=cleaned_target,
                input_bindings=input_bindings,
                action_type=act.action_type,
                preconditions=act.preconditions,
                postconditions=act.postconditions,
                timeout_seconds=15,
                side_effect_class=side_effect,
                checkpoint_policy=checkpoint_policy,
                description=f"{act.action_type.capitalize()} on {act.target_summary or act.target_type}",
            )
            steps.append(step)

        # Static risk analysis
        risk = ProcedureRiskAnalyzer.analyze(steps)

        # Collect required permissions
        perms = set()
        for s in steps:
            if s.preferred_method == "BROWSER_DOM":
                perms.add("browser:execute")
            else:
                perms.add("desktop:execute")

        proc = ReusableProcedure(
            procedure_id=f"proc_{uuid.uuid4().hex[:12]}",
            version=1,
            name=req.name,
            description=req.description or f"Compiled from recording session {session.session_id}",
            category=req.category or "general",
            parameters=parameters,
            required_permissions=sorted(list(perms)),
            steps=steps,
            risk_assessment=risk,
            validation_status=ProcedureValidationStatus.VALIDATED,
        )

        proc.checksum = proc.calculate_checksum()
        ProcedureValidator.validate(proc)

        return proc
