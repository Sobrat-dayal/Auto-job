"""Applicant profile management REST API endpoints with contact encryption."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import ProfileRepository

router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfileCreateRequest(BaseModel):
    profile_name: str = Field(description="Name or title of applicant profile")
    summary: str | None = Field(default=None, description="Professional summary")
    contact_info: dict[str, Any] | None = Field(default=None, description="Sensitive contact info (encrypted at rest)")
    education: list[dict[str, Any]] | None = Field(default=None, description="Education records")
    experience: list[dict[str, Any]] | None = Field(default=None, description="Work experience records")
    career_preferences: dict[str, Any] | None = Field(default=None, description="Job role and location preferences")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_profile(req: ProfileCreateRequest, _auth: AuthDep) -> dict[str, Any]:
    """Creates an applicant profile, automatically encrypting contact info at rest."""
    async with get_db_session() as session:
        repo = ProfileRepository(session)
        profile = await repo.create_profile(
            profile_name=req.profile_name,
            summary=req.summary,
            contact_info=req.contact_info,
            education=req.education,
            experience=req.experience,
            preferences=req.career_preferences,
        )
        return {
            "id": profile.id,
            "profile_name": profile.profile_name,
            "summary": profile.summary,
            "has_contact_info": bool(profile.contact_info_encrypted),
            "updated_at": profile.updated_at.isoformat(),
        }


@router.get("")
async def list_profiles(_auth: AuthDep, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """Lists applicant profiles without disclosing decrypted contact information."""
    async with get_db_session() as session:
        repo = ProfileRepository(session)
        return await repo.list_profiles(limit=limit, offset=offset)


@router.get("/{profile_id}")
async def get_profile(profile_id: str, _auth: AuthDep) -> dict[str, Any]:
    """Retrieves full applicant profile, decrypting contact info for authorized access."""
    async with get_db_session() as session:
        repo = ProfileRepository(session)
        data = await repo.get_profile(profile_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile '{profile_id}' not found.",
            )
        return data
