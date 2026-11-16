"""Application settings REST API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import SettingsRepository

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingUpdateRequest(BaseModel):
    value: dict[str, Any] = Field(description="JSON dictionary for setting value")
    scope: str = Field(default="user", description="Scope of the setting: user or system")


@router.get("")
async def list_settings(_auth: AuthDep, scope: str | None = None) -> list[dict[str, Any]]:
    """Retrieves all authorized non-sensitive settings."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        records = await repo.list_settings(scope=scope)
        return [
            {
                "key": r.key,
                "value": r.value_json,
                "scope": r.scope,
                "updated_at": r.updated_at.isoformat(),
            }
            for r in records
        ]


@router.get("/{key}")
async def get_setting(key: str, _auth: AuthDep) -> dict[str, Any]:
    """Retrieves a single setting value by key."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        val = await repo.get_setting(key)
        if val is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting '{key}' not found.",
            )
        return {"key": key, "value": val}


@router.patch("/{key}")
async def update_setting(key: str, req: SettingUpdateRequest, _auth: AuthDep) -> dict[str, Any]:
    """Updates or creates an authorized non-sensitive setting."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        setting = await repo.set_setting(key=key, value=req.value, scope=req.scope)
        return {
            "key": setting.key,
            "value": setting.value_json,
            "scope": setting.scope,
            "updated_at": setting.updated_at.isoformat(),
        }
