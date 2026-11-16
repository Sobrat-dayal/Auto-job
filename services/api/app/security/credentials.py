"""Secure credential management using Windows DPAPI and cryptographic vault."""

from dataclasses import dataclass
from typing import Any

from app.security.vault import vault


@dataclass
class CredentialMetadata:
    reference_id: str
    provider: str
    credential_type: str
    status: str
    created_at: str
    last_validated_at: str | None


class SecureCredentialManager:
    """Provides secure credential storage and authorized resolution without exposing plaintext secrets."""

    def __init__(self) -> None:
        pass

    def encrypt_secret(self, secret_value: str, provider: str) -> str:
        """Encrypts a secret using the vault with provider bound as associated data."""
        return vault.encrypt_string(secret_value, associated_data=provider)

    def decrypt_secret(self, encrypted_blob: str, provider: str) -> str:
        """Decrypts a secret previously protected by the vault."""
        return vault.decrypt_string(encrypted_blob, associated_data=provider)

    def sanitize_credential_display(self, provider: str, cred_type: str) -> dict[str, Any]:
        """Returns safe non-sensitive representation of configured credentials for API responses."""
        return {
            "provider": provider,
            "credential_type": cred_type,
            "is_configured": True,
            "status": "ready",
        }


credential_manager = SecureCredentialManager()
