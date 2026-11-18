"""Authentication and profile state security for browser automation."""

import base64
import json
import logging
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.security.dpapi import dpapi_protect, dpapi_unprotect

logger = logging.getLogger(__name__)


class BrowserAuthenticationManager:
    """Manages encrypted storage of browser session profiles and interactive auth handoffs."""

    def __init__(self, profiles_dir: Path | None = None) -> None:
        self.profiles_dir = profiles_dir or settings.browser_profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def get_profile_state_path(self, profile_id: str) -> Path:
        """Returns the encrypted storage state file path for a profile."""
        return self.profiles_dir / f"{profile_id}.state.enc"

    def save_storage_state(self, profile_id: str, state_data: dict[str, Any]) -> str:
        """Encrypts and persists Playwright browser storage_state (cookies, origins, tokens)."""
        file_path = self.get_profile_state_path(profile_id)
        raw_bytes = json.dumps(state_data).encode("utf-8")
        try:
            encrypted_bytes = dpapi_protect(raw_bytes, description=f"AUTONOM_BROWSER_PROFILE_{profile_id}")
            encrypted_payload = base64.b64encode(encrypted_bytes).decode("utf-8")
        except Exception as exc:
            logger.warning(f"Could not encrypt profile state with Windows DPAPI, saving encoded: {exc}")
            encrypted_payload = base64.b64encode(raw_bytes).decode("utf-8")

        file_path.write_text(encrypted_payload, encoding="utf-8")
        logger.info(f"Saved secure browser storage state for profile {profile_id}")
        return str(file_path)

    def load_storage_state(self, profile_id: str) -> dict[str, Any] | None:
        """Loads and decrypts Playwright storage_state for a profile."""
        file_path = self.get_profile_state_path(profile_id)
        if not file_path.exists():
            return None

        encrypted_payload = file_path.read_text(encoding="utf-8")
        try:
            encrypted_bytes = base64.b64decode(encrypted_payload)
            decrypted_bytes = dpapi_unprotect(encrypted_bytes)
            return json.loads(decrypted_bytes.decode("utf-8"))
        except Exception as exc:
            logger.error(f"Failed to decrypt/parse storage state for profile {profile_id}: {exc}")
            # Try raw json fallback if unencrypted
            try:
                return json.loads(encrypted_payload)
            except Exception:
                return None

    def export_temporary_state_file(self, profile_id: str) -> str | None:
        """Writes decrypted state to a temporary JSON file for Playwright browser context initialization."""
        state = self.load_storage_state(profile_id)
        if not state:
            return None
        temp_path = self.profiles_dir / f"{profile_id}.temp_state.json"
        temp_path.write_text(json.dumps(state), encoding="utf-8")
        return str(temp_path)

    def cleanup_temporary_state_file(self, profile_id: str) -> None:
        """Removes unencrypted temporary state files created for Playwright launch."""
        temp_path = self.profiles_dir / f"{profile_id}.temp_state.json"
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as exc:
                logger.warning(f"Could not remove temp state file {temp_path}: {exc}")
