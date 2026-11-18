"""Security and origin validation tests for Stage 16 Browser Automation."""

import pytest
from app.browser.security.origins import OriginValidator
from app.browser.security.authentication import BrowserAuthenticationManager


def test_origin_validator_blocks_dangerous_schemes():
    validator = OriginValidator(allow_loopback=False, allow_private_ips=False)

    # File scheme
    res = validator.validate_url("file:///C:/Windows/System32/drivers/etc/hosts")
    assert not res.is_allowed
    assert res.risk_level == "critical"
    assert "Blocked scheme" in res.rejection_reason

    # Javascript scheme
    res = validator.validate_url("javascript:alert(1)")
    assert not res.is_allowed
    assert res.risk_level == "critical"

    # Chrome internal scheme
    res = validator.validate_url("chrome://settings")
    assert not res.is_allowed
    assert res.risk_level == "critical"


def test_origin_validator_blocks_cloud_metadata_endpoints():
    validator = OriginValidator(allow_loopback=False, allow_private_ips=False)

    # AWS / Azure / GCP metadata IP
    res = validator.validate_url("http://169.254.169.254/latest/meta-data/")
    assert not res.is_allowed
    assert res.is_metadata_endpoint
    assert res.risk_level == "critical"

    # Google Cloud internal hostname
    res = validator.validate_url("http://metadata.google.internal/computeMetadata/v1/")
    assert not res.is_allowed
    assert res.is_metadata_endpoint
    assert res.risk_level == "critical"


def test_origin_validator_blocks_private_ips():
    validator = OriginValidator(allow_loopback=False, allow_private_ips=False)

    # Class A private network
    res = validator.validate_url("http://10.0.0.1/admin")
    assert not res.is_allowed
    assert res.is_private_ip

    # Class C private network
    res = validator.validate_url("http://192.168.1.1:8080/")
    assert not res.is_allowed
    assert res.is_private_ip


def test_origin_validator_loopback_policy():
    # Loopback disabled
    strict = OriginValidator(allow_loopback=False)
    res = strict.validate_url("http://127.0.0.1:8765/api/v1/health")
    assert not res.is_allowed
    assert res.is_loopback

    # Loopback enabled for test fixtures
    permissive = OriginValidator(allow_loopback=True)
    res = permissive.validate_url("http://127.0.0.1:8765/api/v1/health")
    assert res.is_allowed
    assert res.is_loopback


def test_origin_validator_domain_allowlist():
    validator = OriginValidator(
        allow_loopback=False,
        allowed_domains={"greenhouse.io", "lever.co"},
    )

    # Allowed domain
    res = validator.validate_url("https://boards.greenhouse.io/anthropic/jobs/123")
    assert res.is_allowed

    # Disallowed domain
    res = validator.validate_url("https://unapproved-portal.example.com")
    assert not res.is_allowed
    assert "not in the allowed domains list" in res.rejection_reason


def test_origin_validator_about_blank():
    validator = OriginValidator()
    res = validator.validate_url("about:blank")
    assert res.is_allowed
    assert res.normalized_url == "about:blank"


def test_browser_authentication_manager_encryption(tmp_path):
    mgr = BrowserAuthenticationManager(profiles_dir=tmp_path)
    state = {
        "cookies": [{"name": "session_token", "value": "secret_abc123", "domain": ".example.com"}],
        "origins": [],
    }

    # Save state
    file_path = mgr.save_storage_state("test_profile_1", state)
    assert tmp_path.joinpath("test_profile_1.state.enc").exists()

    # Load state
    loaded = mgr.load_storage_state("test_profile_1")
    assert loaded is not None
    assert loaded["cookies"][0]["value"] == "secret_abc123"

    # Export temp file and cleanup
    temp_file = mgr.export_temporary_state_file("test_profile_1")
    assert temp_file is not None
    mgr.cleanup_temporary_state_file("test_profile_1")
    assert not tmp_path.joinpath("test_profile_1.temp_state.json").exists()
