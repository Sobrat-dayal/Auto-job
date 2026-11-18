"""Unit tests for Stage 22 security controls, secret redaction, and source filtering."""

import pytest
from app.recruitment.github.source.filters import SourceFilter
from app.recruitment.github.source.secrets import SecretRedactor


def test_secret_redactor_private_key():
    raw = """
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA0Y1+examplePrivateDataKey123456789==
    -----END RSA PRIVATE KEY-----
    """
    assert SecretRedactor.contains_secret(raw) is True
    redacted, has_redactions = SecretRedactor.redact(raw)
    assert has_redactions is True
    assert "BEGIN RSA PRIVATE KEY" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_secret_redactor_github_tokens():
    raw = "GITHUB_TOKEN = 'ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'"
    assert SecretRedactor.contains_secret(raw) is True
    redacted, has_redactions = SecretRedactor.redact(raw)
    assert has_redactions is True
    assert "ghp_ABCDEF" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_secret_redactor_aws_credentials():
    raw = "export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    assert SecretRedactor.contains_secret(raw) is True
    redacted, has_redactions = SecretRedactor.redact(raw)
    assert has_redactions is True
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_secret_redactor_database_url():
    raw = "DATABASE_URL=postgres://app_user:super_secret_password_123@db.prod.internal:5432/main_db"
    assert SecretRedactor.contains_secret(raw) is True
    redacted, has_redactions = SecretRedactor.redact(raw)
    assert has_redactions is True
    assert "super_secret_password_123" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_source_filter_allowed_and_ignored_paths():
    # Manifest files must be allowed
    assert SourceFilter.should_inspect_file("package.json", size_bytes=1200) is True
    assert SourceFilter.should_inspect_file("pyproject.toml", size_bytes=800) is True
    assert SourceFilter.should_inspect_file("Cargo.toml", size_bytes=2400) is True

    # Ignored directories must be rejected
    assert SourceFilter.should_inspect_file("node_modules/lodash/package.json", size_bytes=1000) is False
    assert SourceFilter.should_inspect_file(".git/config", size_bytes=200) is False
    assert SourceFilter.should_inspect_file("target/debug/build.rs", size_bytes=500) is False
    assert SourceFilter.should_inspect_file("__pycache__/main.cpython-312.pyc", size_bytes=3000) is False

    # Binary files must be rejected
    assert SourceFilter.should_inspect_file("app.exe", size_bytes=100000) is False
    assert SourceFilter.should_inspect_file("logo.png", size_bytes=4000) is False
    assert SourceFilter.should_inspect_file("bundle.zip", size_bytes=20000) is False

    # Oversized files (> 500 KB) must be rejected
    assert SourceFilter.should_inspect_file("large_dataset.json", size_bytes=600 * 1024) is False


def test_source_filter_path_traversal_rejection():
    assert SourceFilter.is_safe_relative_path("src/core/router.py") is True
    assert SourceFilter.is_safe_relative_path("../../../etc/passwd") is False
    assert SourceFilter.is_safe_relative_path("..\\..\\Windows\\System32") is False
    assert SourceFilter.is_safe_relative_path("/root/secret.env") is False
