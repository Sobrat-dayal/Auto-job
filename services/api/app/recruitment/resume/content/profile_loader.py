"""Profile Snapshot Loader for Resume Content Engine (Stage 23)."""

from __future__ import annotations

import logging
from typing import Any, Optional
from app.core.security import AuthContext
from app.recruitment.profile.contracts import ApplicantProfile, ProfileSnapshot
from app.recruitment.profile.service import applicant_profile_service
from app.recruitment.resume.errors import ResumeError

logger = logging.getLogger("autonom.recruitment.resume.content.profile_loader")


class ProfileSnapshotLoader:
    """Loads and encapsulates fixed applicant profile snapshots for resume generation."""

    @classmethod
    def load_profile(cls, profile_id: str, auth: Optional[AuthContext] = None) -> ApplicantProfile:
        try:
            return applicant_profile_service.get_profile(profile_id, auth=auth)
        except Exception as exc:
            logger.error(f"Failed to load applicant profile '{profile_id}': {exc}")
            raise ResumeError(f"Could not load applicant profile '{profile_id}': {exc}") from exc

    @classmethod
    def capture_snapshot(cls, profile_id: str, auth: Optional[AuthContext] = None) -> ProfileSnapshot:
        try:
            return applicant_profile_service.create_snapshot(
                profile_id=profile_id,
                target_agent="resume_agent",
                scopes=["skills", "education", "experience", "projects", "certifications", "contact"],
                auth=auth,
            )
        except Exception as exc:
            logger.error(f"Failed to capture snapshot for '{profile_id}': {exc}")
            raise ResumeError(f"Could not capture profile snapshot: {exc}") from exc
