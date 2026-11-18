"""Privacy protection and scope filtering for computer action recording."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("autonom.reliability.privacy")

# Regex patterns matching sensitive keys and values
SENSITIVE_KEY_PATTERNS = [
    re.compile(r"pass(word)?", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"auth(orization)?", re.IGNORECASE),
    re.compile(r"bearer", re.IGNORECASE),
    re.compile(r"credit[_-]?card", re.IGNORECASE),
    re.compile(r"cvv|cvc", re.IGNORECASE),
    re.compile(r"ssn|social[_-]?security", re.IGNORECASE),
]

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"^ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}$"),  # JWT
    re.compile(r"^(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}$"),  # GitHub Token
    re.compile(r"^sk-[A-Za-z0-9]{32,}$"),  # OpenAI key
]


class RecordingPrivacyFilter:
    """Sanitizes action parameters and filters actions by application/origin scopes."""

    def __init__(
        self,
        allowed_app_scopes: Optional[List[str]] = None,
        allowed_web_origins: Optional[List[str]] = None,
    ) -> None:
        self.allowed_app_scopes = [s.lower().strip() for s in (allowed_app_scopes or [])]
        self.allowed_web_origins = [o.lower().strip() for o in (allowed_web_origins or [])]

    def is_app_allowed(self, app_name: str) -> bool:
        """Check if an application process name is allowed."""
        if not self.allowed_app_scopes:
            return True
        clean = app_name.lower().strip()
        return any(clean == allowed or clean.endswith(f"\\{allowed}") for allowed in self.allowed_app_scopes)

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if a web origin is allowed."""
        if not self.allowed_web_origins:
            return True
        clean = origin.lower().strip()
        return any(clean.startswith(allowed) for allowed in self.allowed_web_origins)

    def filter_parameters(self, parameters: Dict[str, Any], target_identity: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], bool]:
        """Filter parameters and return (sanitized_dict, is_sensitive)."""
        target_id = target_identity or {}
        sanitized = self.sanitize_parameters("general", parameters, target_id)
        is_sensitive = any(
            "[REDACTED" in str(v) for v in sanitized.values()
        )
        return sanitized, is_sensitive

    def is_target_in_scope(self, target_identity: Dict[str, Any]) -> Tuple[bool, str]:
        """Verify whether an action target falls within authorized application/origin bounds."""
        # 1. Check native process/window scope
        proc_name = target_identity.get("process_name")
        if proc_name and self.allowed_app_scopes:
            clean_proc = str(proc_name).lower().strip()
            if not any(clean_proc == allowed or clean_proc.endswith(f"\\{allowed}") for allowed in self.allowed_app_scopes):
                return False, f"Process '{proc_name}' is outside approved application scopes."

        # 2. Check web origin scope
        page_url = target_identity.get("url") or target_identity.get("origin")
        if page_url and self.allowed_web_origins:
            clean_url = str(page_url).lower().strip()
            if not any(clean_url.startswith(allowed) for allowed in self.allowed_web_origins):
                return False, f"Origin '{page_url}' is outside approved web origin scopes."

        return True, "In scope"

    def sanitize_parameters(self, action_type: str, parameters: Dict[str, Any], target_identity: Dict[str, Any]) -> Dict[str, Any]:
        """Redact passwords, secret tokens, and sensitive fields from action parameters."""
        sanitized: Dict[str, Any] = {}

        # Check if target itself is a password field
        is_password_target = False
        target_name = str(target_identity.get("element_name") or target_identity.get("dom_selector") or "").lower()
        control_type = str(target_identity.get("control_type") or "").lower()
        if "password" in target_name or "passwd" in target_name or "password" in control_type:
            is_password_target = True

        for k, v in parameters.items():
            k_lower = k.lower()

            # Rule 1: Key matches sensitive keyword
            if any(p.search(k_lower) for p in SENSITIVE_KEY_PATTERNS) or is_password_target:
                if "pass" in k_lower or is_password_target:
                    sanitized[k] = "[REDACTED_PASSWORD]"
                elif any(tok in k_lower for tok in ("token", "key", "auth", "secret", "bearer")):
                    sanitized[k] = "[REDACTED_TOKEN]"
                else:
                    sanitized[k] = "[REDACTED_SECRET]"
                continue

            # Rule 2: Value string matches sensitive regex
            if isinstance(v, str):
                if any(p.search(v) for p in SENSITIVE_VALUE_PATTERNS):
                    sanitized[k] = "[REDACTED_TOKEN]"
                    continue
                # If text entry into a field named password
                if (k_lower in ("text", "input_text", "value")) and is_password_target:
                    sanitized[k] = "[REDACTED_PASSWORD]"
                    continue

            sanitized[k] = v

        return sanitized
