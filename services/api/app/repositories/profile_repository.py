"""Repository for applicant profiles with field-level contact encryption."""

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import ApplicantProfile
from app.repositories.base import BaseRepository
from app.security.vault import vault


class ProfileRepository(BaseRepository[ApplicantProfile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_profile(
        self,
        profile_name: str,
        summary: str | None = None,
        contact_info: dict[str, Any] | None = None,
        education: list[dict[str, Any]] | None = None,
        experience: list[dict[str, Any]] | None = None,
        preferences: dict[str, Any] | None = None,
        profile_id: str | None = None,
    ) -> ApplicantProfile:
        from app.db.models import generate_uuid

        pid = profile_id or generate_uuid()
        profile = ApplicantProfile(
            id=pid,
            profile_name=profile_name,
            summary=summary,
            education_json=education or [],
            experience_json=experience or [],
            career_preferences_json=preferences or {},
        )

        if contact_info:
            plain_json = json.dumps(contact_info)
            profile.contact_info_encrypted = vault.encrypt_string(plain_json, associated_data=pid)

        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_profile(self, profile_id: str, decrypt_contact: bool = True) -> dict[str, Any] | None:
        query = (
            select(ApplicantProfile)
            .where(ApplicantProfile.id == profile_id)
            .options(
                selectinload(ApplicantProfile.skills),
                selectinload(ApplicantProfile.evidence),
                selectinload(ApplicantProfile.resumes),
            )
        )
        result = await self.session.execute(query)
        profile = result.scalar_one_or_none()
        if not profile:
            return None

        contact_data = None
        if decrypt_contact and profile.contact_info_encrypted:
            try:
                decrypted = vault.decrypt_string(profile.contact_info_encrypted, associated_data=profile.id)
                contact_data = json.loads(decrypted)
            except Exception:
                contact_data = {"error": "Failed to decrypt contact info"}

        return {
            "id": profile.id,
            "profile_name": profile.profile_name,
            "summary": profile.summary,
            "contact_info": contact_data,
            "education": profile.education_json,
            "experience": profile.experience_json,
            "career_preferences": profile.career_preferences_json,
            "skills": [
                {
                    "id": s.id,
                    "skill_name": s.skill_name,
                    "category": s.category,
                    "confidence": s.confidence,
                }
                for s in profile.skills
            ],
            "resumes": [
                {
                    "id": r.id,
                    "version_tag": r.version_tag,
                    "template_id": r.template_id,
                    "artifact_ref": r.artifact_ref,
                }
                for r in profile.resumes
            ],
            "updated_at": profile.updated_at.isoformat(),
        }

    async def list_profiles(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        query = select(ApplicantProfile).order_by(ApplicantProfile.updated_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        profiles = result.scalars().all()

        return [
            {
                "id": p.id,
                "profile_name": p.profile_name,
                "summary": p.summary,
                "has_contact_info": bool(p.contact_info_encrypted),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in profiles
        ]
