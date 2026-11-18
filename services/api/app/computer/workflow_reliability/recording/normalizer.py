"""Action event normalizer across Browser DOM, Windows UIA, Win32, and Visual Grounding."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.computer.workflow_reliability.contracts import RecordedAction


class ActionEventNormalizer:
    """Transforms multi-adapter computer actions into normalized RecordedAction contracts."""

    @staticmethod
    def normalize(
        session_id: str,
        sequence_index: int,
        source_adapter: str,
        action_type: str,
        target_summary: str,
        target_identity: Dict[str, Any],
        parameters: Dict[str, Any],
        verification_status: str = "success",
        execution_time_ms: float = 0.0,
        routing_metadata: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = "windows_computer_agent",
        error_message: Optional[str] = None,
    ) -> RecordedAction:
        """Create a canonical RecordedAction instance."""
        target_type = target_identity.get("target_type") or "unknown"
        if not target_type or target_type == "unknown":
            if "dom_selector" in target_identity or source_adapter == "BROWSER_DOM":
                target_type = "BROWSER_ELEMENT"
            elif "uia_runtime_id" in target_identity or source_adapter == "WINDOWS_UIA":
                target_type = "UIA_ELEMENT"
            elif "window_handle" in target_identity or source_adapter == "WINDOWS_WIN32":
                target_type = "NATIVE_WINDOW"
            elif "coordinates" in target_identity or source_adapter == "VISUAL_GROUNDING":
                target_type = "VISUAL_TARGET"

        # Construct automatic default preconditions and postconditions
        preconditions = []
        if target_identity.get("window_title"):
            preconditions.append({
                "type": "window_title_match",
                "expected": target_identity["window_title"],
            })
        if target_identity.get("dom_selector"):
            preconditions.append({
                "type": "dom_selector_exists",
                "selector": target_identity["dom_selector"],
            })

        postconditions = [{
            "type": "mutation_verified",
            "verification_status": verification_status,
        }]

        return RecordedAction(
            sequence_index=sequence_index,
            session_id=session_id,
            source_adapter=source_adapter,
            capability_id="hybrid_execute",
            workflow_id=workflow_id,
            task_id=task_id,
            agent_id=agent_id,
            target_type=str(target_type),
            target_summary=target_summary,
            target_identity=target_identity,
            action_type=action_type,
            approved_parameters=parameters,
            preconditions=preconditions,
            postconditions=postconditions,
            execution_timestamp=datetime.now(timezone.utc),
            result_status="success" if not error_message else "failed",
            verification_outcome=verification_status,
            execution_time_ms=execution_time_ms,
            error_message=error_message,
            routing_metadata=routing_metadata or {},
        )
