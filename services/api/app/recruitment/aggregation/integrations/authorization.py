"""Stage 14 Authorization & Scope Validation for Aggregation (Stage 27)."""

from typing import Optional
from app.core.security import AuthContext
from app.recruitment.aggregation.errors import AuthorizationDeniedError


REQUIRED_PERMISSIONS = {
    "read_canonical": "recruitment.jobs.canonical.read",
    "create_canonical": "recruitment.jobs.canonical.create",
    "update_canonical": "recruitment.jobs.canonical.update",
    "merge_jobs": "recruitment.jobs.merge",
    "split_jobs": "recruitment.jobs.split",
    "duplicate_review": "recruitment.jobs.duplicate_review",
    "read_employers": "recruitment.employers.read",
    "resolve_employers": "recruitment.employers.resolve",
    "correct_employers": "recruitment.employers.correct",
}


def verify_aggregation_permission(auth: Optional[AuthContext], operation: str) -> bool:
    """Validate that the requesting context has the required permission."""
    if not auth:
        return True

    # Primary local desktop operator or admin has full operational access
    if getattr(auth, "client_id", None) == "autonom-desktop-local" or getattr(auth, "is_admin", False):
        return True

    required = REQUIRED_PERMISSIONS.get(operation)
    if not required:
        return True

    # For scoped callers, check granular or wildcard scopes
    scopes = getattr(auth, "scopes", None)
    if scopes and required not in scopes and "*" not in scopes and "recruitment.*" not in scopes:
        raise AuthorizationDeniedError(f"Missing required permission: {required}")

    return True
