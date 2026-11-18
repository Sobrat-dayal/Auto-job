"""Stage 14 Authorization Engine integration and permission enforcement for Applicant Profiles."""

from __future__ import annotations

import logging
from typing import Optional

from app.core.security import AuthContext
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.profile.errors import ProfilePermissionDeniedError

logger = logging.getLogger("autonom.recruitment.profile.integrations.auth")

# Canonical Stage 21 Permission Scopes
SCOPE_PROFILE_READ = "applicant.profile.read"
SCOPE_PROFILE_UPDATE = "applicant.profile.update"
SCOPE_PROFILE_DELETE = "applicant.profile.delete"
SCOPE_IDENTITY_READ = "applicant.identity.read"
SCOPE_CONTACT_READ = "applicant.contact.read"
SCOPE_EDUCATION_READ = "applicant.education.read"
SCOPE_EXPERIENCE_READ = "applicant.experience.read"
SCOPE_SKILLS_READ = "applicant.skills.read"
SCOPE_PROJECTS_READ = "applicant.projects.read"
SCOPE_EVIDENCE_READ = "applicant.evidence.read"
SCOPE_EVIDENCE_UPLOAD = "applicant.evidence.upload"
SCOPE_EVIDENCE_DELETE = "applicant.evidence.delete"
SCOPE_CLAIMS_CONFIRM = "applicant.claims.confirm"
SCOPE_PROFILE_EXPORT = "applicant.profile.export"
SCOPE_ELIGIBILITY_READ = "applicant.eligibility.read"


class ProfileAuthorizationEnforcer:
    """Enforces fine-grained permission scopes and profile ownership boundaries."""

    @classmethod
    def check_ownership(cls, profile: ApplicantProfile, auth: Optional[AuthContext]) -> None:
        """Ensures that the calling client owns the target profile or possesses system elevation."""
        if not auth:
            return  # Internal or local development fallback
        if getattr(auth, "is_admin", False) or auth.client_id in ("system", "supervisor_agent", "admin", "autonom-desktop-local"):
            return
        if profile.owner_id and profile.owner_id not in (auth.client_id, "default_user"):
            logger.warning(
                f"Ownership violation: Actor '{auth.client_id}' attempted to access profile owned by '{profile.owner_id}'."
            )
            raise ProfilePermissionDeniedError(
                f"Access denied: Profile '{profile.id}' belongs to another user."
            )

    @classmethod
    def check_permission(cls, required_scope: str, auth: Optional[AuthContext]) -> None:
        """Validates that the active client context possesses the required permission scope."""
        if not auth:
            return
        if getattr(auth, "is_admin", False) or auth.client_id in ("system", "supervisor_agent", "admin", "autonom-desktop-local"):
            return
        # If client has specific scopes declared, assert presence
        if hasattr(auth, "scopes") and auth.scopes:
            if required_scope not in auth.scopes and "*" not in auth.scopes and "applicant.*" not in auth.scopes:
                logger.warning(f"Permission denied: Actor '{auth.client_id}' missing scope '{required_scope}'.")
                raise ProfilePermissionDeniedError(
                    f"Permission denied: Required scope '{required_scope}' is not granted."
                )
