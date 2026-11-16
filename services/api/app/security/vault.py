"""Authenticated encryption vault using AES-256-GCM with Windows DPAPI key wrapping."""

import base64
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings
from app.security.dpapi import dpapi_protect, dpapi_unprotect


class CryptographicVault:
    """Manages field-level and artifact-level AES-256-GCM encryption with Windows DPAPI key protection."""

    def __init__(self, key_file_path: Path | None = None) -> None:
        self._key_file_path = key_file_path or (settings.config_dir / ".vault.key")
        self._aesgcm: AESGCM | None = None

    def initialize(self) -> None:
        """Initializes or loads the DPAPI-wrapped 256-bit AES master key."""
        if self._aesgcm is not None:
            return

        self._key_file_path.parent.mkdir(parents=True, exist_ok=True)

        if self._key_file_path.exists():
            encrypted_key = self._key_file_path.read_bytes()
            raw_key = dpapi_unprotect(encrypted_key)
        else:
            raw_key = AESGCM.generate_key(bit_length=256)
            encrypted_key = dpapi_protect(raw_key, description="AUTONOM_VAULT_KEY")
            self._key_file_path.write_bytes(encrypted_key)

        self._aesgcm = AESGCM(raw_key)

    @property
    def is_initialized(self) -> bool:
        return self._aesgcm is not None

    def encrypt_bytes(self, plaintext: bytes, associated_data: bytes | None = None) -> bytes:
        """Encrypts bytes using AES-256-GCM returning nonce (12 bytes) + ciphertext/tag."""
        if self._aesgcm is None:
            self.initialize()
        assert self._aesgcm is not None

        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext

    def decrypt_bytes(self, payload: bytes, associated_data: bytes | None = None) -> bytes:
        """Decrypts bytes payload containing 12-byte nonce followed by ciphertext and auth tag."""
        if self._aesgcm is None:
            self.initialize()
        assert self._aesgcm is not None

        if len(payload) < 28:
            raise ValueError("Invalid payload: shorter than minimum nonce + auth tag length")

        nonce = payload[:12]
        ciphertext = payload[12:]
        return self._aesgcm.decrypt(nonce, ciphertext, associated_data)

    def encrypt_string(self, plaintext: str, associated_data: str | None = None) -> str:
        """Encrypts string returning a URL-safe base64 string."""
        ad_bytes = associated_data.encode("utf-8") if associated_data else None
        cipher_bytes = self.encrypt_bytes(plaintext.encode("utf-8"), ad_bytes)
        return base64.urlsafe_b64encode(cipher_bytes).decode("ascii")

    def decrypt_string(self, ciphertext_b64: str, associated_data: str | None = None) -> str:
        """Decrypts URL-safe base64 string returning original plaintext string."""
        ad_bytes = associated_data.encode("utf-8") if associated_data else None
        raw_bytes = base64.urlsafe_b64decode(ciphertext_b64.encode("ascii"))
        plain_bytes = self.decrypt_bytes(raw_bytes, ad_bytes)
        return plain_bytes.decode("utf-8")


vault = CryptographicVault()
