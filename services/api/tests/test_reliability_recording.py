"""Unit tests for Stage 20 Action Recording, Normalization, Privacy, and Integrity."""

import pytest
from app.computer.workflow_reliability.contracts import (
    RecordingMode,
    RecordingStatus,
    StartRecordingRequest,
)
from app.computer.workflow_reliability.errors import (
    RecordingActiveError,
    RecordingClosedError,
    RecordingScopeExceededError,
)
from app.computer.workflow_reliability.recording.privacy import RecordingPrivacyFilter
from app.computer.workflow_reliability.service import WorkflowReliabilityService


def test_privacy_filter_redacts_sensitive_keys_and_values():
    filter_engine = RecordingPrivacyFilter()
    raw_params = {
        "user_email": "engineer@autonom.ai",
        "password": "SuperSecretPassword123!",
        "api_key": "sk-autonom-token-abcdef",
        "search_term": "python jobs",
    }
    cleaned, is_sensitive = filter_engine.filter_parameters(raw_params)
    assert is_sensitive is True
    assert cleaned["user_email"] == "engineer@autonom.ai"
    assert cleaned["search_term"] == "python jobs"
    assert cleaned["password"] == "[REDACTED_PASSWORD]"
    assert cleaned["api_key"] == "[REDACTED_TOKEN]"


def test_privacy_filter_validates_scopes():
    filter_engine = RecordingPrivacyFilter(
        allowed_app_scopes=["notepad.exe", "calc.exe"],
        allowed_web_origins=["https://jobs.example.com"],
    )
    # Valid targets
    assert filter_engine.is_app_allowed("notepad.exe") is True
    assert filter_engine.is_origin_allowed("https://jobs.example.com") is True

    # Invalid targets
    assert filter_engine.is_app_allowed("powershell.exe") is False
    assert filter_engine.is_origin_allowed("https://malicious.com") is False


def test_recording_lifecycle():
    service = WorkflowReliabilityService()
    req = StartRecordingRequest(
        name="Test Workflow Recording",
        allowed_app_scopes=["notepad.exe"],
        allowed_web_origins=["https://jobs.example.com"],
    )
    session = service.start_recording(req)
    assert session.status == RecordingStatus.ACTIVE
    assert session.session_id.startswith("recsess_") or session.session_id.startswith("rec_")

    # Cannot start another session while active
    with pytest.raises(RecordingActiveError):
        service.start_recording(req)

    # Record action
    action = service.record_action(
        session_id=session.session_id,
        source_adapter="desktop",
        action_type="type_text",
        raw_parameters={"text": "Hello Autonom", "password": "hidden_secret_123"},
        application_name="notepad.exe",
    )
    assert action.sequence_number == 1
    assert action.is_sensitive is True
    assert action.normalized_parameters["password"] == "[REDACTED_PASSWORD]"

    # Pause and Resume
    paused = service.pause_recording(session.session_id)
    assert paused.status == RecordingStatus.PAUSED

    resumed = service.resume_recording(session.session_id)
    assert resumed.status == RecordingStatus.ACTIVE

    # Stop and Seal
    stopped = service.stop_recording(session.session_id)
    assert stopped.status == RecordingStatus.STOPPED
    assert stopped.integrity_hash is not None
    assert len(stopped.integrity_hash) == 64  # SHA-256 length

    # Cannot record into stopped session
    with pytest.raises(RecordingClosedError):
        service.record_action(
            session_id=session.session_id,
            source_adapter="desktop",
            action_type="click",
            application_name="notepad.exe",
        )
