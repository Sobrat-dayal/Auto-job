"""Security utilities, authentication dependency, and sensitive data redaction."""

import re
from typing import Any

from fastapi import Depends, Header, Query, Request
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AuthenticationError

SENSITIVE_KEY_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|auth|password|secret|credential|cookie|private[_-]?key|session)"
)


class AuthContext(BaseModel):
    """Authenticated context passed to protected endpoint handlers."""

    client_id: str
    authenticated: bool
    scopes: list[str] = ["tasks:read", "tasks:write", "events:read", "system:read"]


def redact_sensitive_data(obj: Any) -> Any:
    """Recursively redacts sensitive keys and values from dictionaries and objects for safe logging."""
    if isinstance(obj, dict):
        redacted = {}
        for key, val in obj.items():
            if SENSITIVE_KEY_PATTERN.search(str(key)):
                redacted[key] = "[REDACTED]"
            elif isinstance(val, (dict, list)):
                redacted[key] = redact_sensitive_data(val)
            else:
                redacted[key] = val
        return redacted
    if isinstance(obj, list):
        return [redact_sensitive_data(item) for item in obj]
    return obj


def extract_token_from_request(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    token_param: str | None = Query(default=None, alias="token"),
) -> str | None:
    """Extracts authentication token from Authorization header, X-API-Key header, or ?token= query parameter."""
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    if x_api_key:
        return x_api_key.strip()
    if token_param:
        return token_param.strip()
    # Check query params directly from URL if not caught
    return request.query_params.get("token")


async def require_auth(
    token: str | None = Depends(extract_token_from_request),
) -> AuthContext:
    """FastAPI dependency enforcing local token authentication for operational endpoints."""
    if not token or token != settings.api_key:
        raise AuthenticationError("Invalid or missing API token.")

    return AuthContext(
        client_id="autonom-desktop-local",
        authenticated=True,
        scopes=["tasks:read", "tasks:write", "events:read", "system:read"],
    )
