"""Central Action Recording Manager for structured computer interactions."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.computer.workflow_reliability.contracts import (
    RecordedAction,
    RecordingMode,
    RecordingSession,
    RecordingStatus,
    StartRecordingRequest,
)
from app.computer.workflow_reliability.errors import (
    RecordingActiveError,
    RecordingClosedError,
    RecordingError,
    RecordingScopeExceededError,
)
from app.computer.workflow_reliability.recording.finalizer import RecordingFinalizer
from app.computer.workflow_reliability.recording.normalizer import ActionEventNormalizer
from app.computer.workflow_reliability.recording.privacy import RecordingPrivacyFilter

logger = logging.getLogger("autonom.reliability.recording_manager")


class ActionRecordingManager:
    """Manages recording session lifecycles, action capture, and scope privacy enforcement."""

    def __init__(self) -> None:
        self._sessions: Dict[str, RecordingSession] = {}
        self._actions: Dict[str, List[RecordedAction]] = {}
        self._privacy_filters: Dict[str, RecordingPrivacyFilter] = {}
        self._active_session_id: Optional[str] = None

    @property
    def active_session_id(self) -> Optional[str]:
        return self._active_session_id

    def start_recording(self, req: StartRecordingRequest) -> RecordingSession:
        """Start a new structured computer recording session."""
        if self._active_session_id:
            active = self._sessions.get(self._active_session_id)
            if active and active.status in (RecordingStatus.ACTIVE, RecordingStatus.RECORDING):
                raise RecordingActiveError(
                    f"A recording session is already active ({self._active_session_id}). Stop or pause it first."
                )

        session = RecordingSession(
            name=req.name or "Interactive Procedure Recording",
            mode=req.mode,
            status=RecordingStatus.ACTIVE,
            workflow_id=req.workflow_id,
            agent_id=req.agent_id,
            allowed_app_scopes=req.allowed_app_scopes,
            allowed_web_origins=req.allowed_web_origins,
            metadata=req.metadata,
        )

        self._sessions[session.session_id] = session
        self._actions[session.session_id] = []
        self._privacy_filters[session.session_id] = RecordingPrivacyFilter(
            allowed_app_scopes=req.allowed_app_scopes,
            allowed_web_origins=req.allowed_web_origins,
        )
        self._active_session_id = session.session_id

        logger.info("Recording session started: %s (%s)", session.session_id, session.name)
        return session

    def pause_recording(self, session_id: Optional[str] = None) -> RecordingSession:
        """Pause active recording."""
        sid = session_id or self._active_session_id
        if not sid or sid not in self._sessions:
            raise RecordingError("No active recording session to pause.")

        session = self._sessions[sid]
        if session.status not in (RecordingStatus.ACTIVE, RecordingStatus.RECORDING):
            raise RecordingClosedError(f"Cannot pause session in status '{session.status.value}'.")

        session.status = RecordingStatus.PAUSED
        logger.info("Recording session paused: %s", sid)
        return session

    def resume_recording(self, session_id: Optional[str] = None) -> RecordingSession:
        """Resume a paused recording session."""
        sid = session_id or self._active_session_id
        if not sid or sid not in self._sessions:
            raise RecordingError("No recording session to resume.")

        session = self._sessions[sid]
        if session.status != RecordingStatus.PAUSED:
            raise RecordingClosedError(f"Cannot resume session in status '{session.status.value}'.")

        session.status = RecordingStatus.ACTIVE
        self._active_session_id = sid
        logger.info("Recording session resumed: %s", sid)
        return session

    def stop_recording(self, session_id: Optional[str] = None) -> RecordingSession:
        """Stop, seal, and finalize a recording session."""
        sid = session_id or self._active_session_id
        if not sid or sid not in self._sessions:
            raise RecordingError("No recording session to stop.")

        session = self._sessions[sid]
        session.status = RecordingStatus.STOPPED
        actions = self._actions.get(sid, [])
        finalized_session = RecordingFinalizer.finalize(session, actions)
        finalized_session.status = RecordingStatus.STOPPED

        if self._active_session_id == sid:
            self._active_session_id = None

        logger.info(
            "Recording session finalized: %s (%d actions, hash: %s)",
            sid,
            finalized_session.captured_actions_count,
            finalized_session.integrity_hash[:8] if finalized_session.integrity_hash else "none",
        )
        return finalized_session

    def record_action(
        self,
        source_adapter: str,
        action_type: str,
        target_summary: str = "target",
        target_identity: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        verification_status: str = "success",
        execution_time_ms: float = 0.0,
        routing_metadata: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = "windows_computer_agent",
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        raw_parameters: Optional[Dict[str, Any]] = None,
        application_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[RecordedAction]:
        """Record an executed action into the current or specified recording session."""
        sid = session_id or self._active_session_id
        if not sid or sid not in self._sessions:
            if session_id:
                raise RecordingClosedError(f"Recording session '{session_id}' not found.")
            return None  # No recording session active; pass-through

        session = self._sessions[sid]
        if session.status in (RecordingStatus.STOPPED, RecordingStatus.COMPLETED, RecordingStatus.FINALIZING):
            raise RecordingClosedError(f"Recording session '{sid}' is closed (status: {session.status.value}).")
        if session.status == RecordingStatus.PAUSED:
            raise RecordingClosedError(f"Recording session '{sid}' is paused.")

        t_identity = target_identity or {}
        if application_name and "process_name" not in t_identity:
            t_identity["process_name"] = application_name

        params = parameters if parameters is not None else (raw_parameters or {})

        # Apply privacy and scope filtering
        p_filter = self._privacy_filters.get(sid) or RecordingPrivacyFilter()
        in_scope, reason = p_filter.is_target_in_scope(t_identity)
        if not in_scope:
            session.excluded_events_count += 1
            logger.debug("Action excluded by recording scope filter: %s", reason)
            return None

        clean_params = p_filter.sanitize_parameters(action_type, params, t_identity)
        seq_idx = len(self._actions[sid])

        action = ActionEventNormalizer.normalize(
            session_id=sid,
            sequence_index=seq_idx,
            source_adapter=source_adapter,
            action_type=action_type,
            target_summary=target_summary,
            target_identity=t_identity,
            parameters=clean_params,
            verification_status=verification_status,
            execution_time_ms=execution_time_ms,
            routing_metadata=routing_metadata,
            workflow_id=workflow_id,
            task_id=task_id,
            agent_id=agent_id,
            error_message=error_message,
        )

        self._actions[sid].append(action)
        session.captured_actions_count = len(self._actions[sid])
        return action

    def get_session(self, session_id: str) -> Optional[RecordingSession]:
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[RecordingSession]:
        return list(self._sessions.values())

    def get_session_actions(self, session_id: str) -> List[RecordedAction]:
        return list(self._actions.get(session_id, []))
