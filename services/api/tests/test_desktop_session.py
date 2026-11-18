"""Tests for Desktop Session, Lock Detection, and Workstation State (Stage 17)."""

import pytest
from app.computer.contracts import DesktopSessionInfo, DesktopSessionState
from app.computer.windows.sessions import session_manager


def test_desktop_session_detection():
    """Verify session manager retrieves active Windows desktop session, screen resolution, and desktop name."""
    session = session_manager.get_session_info()

    assert isinstance(session, DesktopSessionInfo)
    assert session.wts_session_id >= 0
    assert session.desktop_name is not None
    assert len(session.desktop_name) > 0
    assert "x" in session.resolution
    assert isinstance(session.is_locked, bool)
    assert session.status in [DesktopSessionState.ACTIVE, DesktopSessionState.LOCKED, DesktopSessionState.UNAVAILABLE]


def test_desktop_session_resolution_and_user():
    """Verify session returns valid username and interactive resolution."""
    session = session_manager.get_session_info()
    assert session.user_name is not None
    parts = session.resolution.split("x")
    assert len(parts) == 2
    assert int(parts[0]) > 0
    assert int(parts[1]) > 0
