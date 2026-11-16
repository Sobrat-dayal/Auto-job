"""Tests for Windows DPAPI key wrapping and AES-256-GCM Cryptographic Vault."""

from pathlib import Path

import pytest

from app.security.dpapi import dpapi_protect, dpapi_unprotect
from app.security.vault import CryptographicVault


def test_dpapi_protect_unprotect():
    original = b"autonom_test_dpapi_secret_42"
    cipher = dpapi_protect(original, description="TEST_SECRET")
    assert cipher != original
    decrypted = dpapi_unprotect(cipher)
    assert decrypted == original


def test_vault_field_encryption(tmp_path: Path):
    vault_key_file = tmp_path / "config" / ".vault.key"
    test_vault = CryptographicVault(key_file_path=vault_key_file)
    test_vault.initialize()

    assert vault_key_file.exists()

    plaintext = "Sensitive contact email: user@autonom.local, phone: +1-555-0199"
    token = test_vault.encrypt_string(plaintext, associated_data="profile-100")
    assert token != plaintext

    decrypted = test_vault.decrypt_string(token, associated_data="profile-100")
    assert decrypted == plaintext

    # Verify tampering or invalid associated data fails
    with pytest.raises(Exception):
        test_vault.decrypt_string(token, associated_data="wrong-profile-id")
