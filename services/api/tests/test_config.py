"""Tests for configuration settings and validation."""

import pytest

from app.core.config import Settings


def test_settings_default_values():
    s = Settings()
    assert s.app_name == "AUTONOM API"
    assert s.host == "127.0.0.1"
    assert s.port == 8765
    assert s.is_loopback is True


def test_invalid_port_validation():
    with pytest.raises(ValueError, match="Port must be between 1024 and 65535"):
        Settings(port=80)

    with pytest.raises(ValueError, match="Port must be between 1024 and 65535"):
        Settings(port=70000)
