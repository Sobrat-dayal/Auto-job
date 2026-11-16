"""Application settings REST API endpoints supporting category management, validation, and schema metadata."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import AuditRepository, SettingsRepository
from app.repositories.settings_repository import CATEGORY_SCHEMA_MAP
from app.schemas.settings import (
    AllSettingsResponse,
    SettingsExportPayload,
    SettingsImportPayload,
    SettingsSchemaMetadataResponse,
)

router = APIRouter(prefix="/settings", tags=["settings"])

SENSITIVE_CATEGORIES = {"permissions", "security", "automation"}


class SettingUpdateRequest(BaseModel):
    value: dict[str, Any] = Field(default_factory=dict, description="JSON dictionary for setting value")
    scope: str = Field(default="system", description="Scope of the setting: user or system")


class CategoryResetRequest(BaseModel):
    category: str = Field(default="all", description="Category name to reset, or 'all'")


@router.get("", response_model=None)
async def list_or_get_settings(
    _auth: AuthDep,
    scope: str | None = None,
    aggregated: bool = Query(default=False, description="Return aggregated 13-category settings object"),
) -> Any:
    """Retrieves all authorized settings. Returns aggregated object if aggregated=True, else list of raw records."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        if aggregated:
            return await repo.get_all_settings()

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


@router.get("/all", response_model=AllSettingsResponse)
async def get_all_aggregated_settings(_auth: AuthDep) -> AllSettingsResponse:
    """Returns the centralized aggregated settings object across all 13 categories with schema defaults."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        return await repo.get_all_settings()


@router.get("/schema", response_model=SettingsSchemaMetadataResponse)
async def get_settings_schema_metadata(_auth: AuthDep) -> SettingsSchemaMetadataResponse:
    """Returns metadata describing settings categories, types, default values, sensitivity, and restart requirements."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        return repo.get_schema_metadata()


@router.get("/export", response_model=SettingsExportPayload)
async def export_non_sensitive_settings(_auth: AuthDep) -> SettingsExportPayload:
    """Exports non-sensitive application settings into a portable, versioned JSON payload."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        export_data = await repo.export_settings()
        return SettingsExportPayload(**export_data)


@router.post("/import")
async def import_settings(payload: SettingsImportPayload, _auth: AuthDep) -> dict[str, Any]:
    """Validates and imports non-sensitive settings, rejecting unknown keys or malformed structures."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        audit_repo = AuditRepository(session)
        try:
            result = await repo.import_settings(payload.model_dump())
            await audit_repo.log_audit(
                action_type="SETTINGS_IMPORT",
                resource_type="app_settings",
                outcome="success",
                metadata={"imported_categories": result["imported_categories"]},
            )
            return result
        except ValueError as exc:
            await audit_repo.log_audit(
                action_type="SETTINGS_IMPORT",
                resource_type="app_settings",
                outcome="failure",
                metadata={"error": str(exc)},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Import validation failed: {exc}",
            ) from exc


@router.post("/reset")
async def reset_settings(req: CategoryResetRequest, _auth: AuthDep) -> dict[str, Any]:
    """Resets one or all settings categories to default values."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        audit_repo = AuditRepository(session)

        if req.category == "all":
            for cat in CATEGORY_SCHEMA_MAP:
                await repo.reset_category(cat)
            await audit_repo.log_audit(
                action_type="SETTINGS_RESET_ALL",
                resource_type="app_settings",
                outcome="success",
            )
            return {"reset": True, "category": "all"}

        if req.category not in CATEGORY_SCHEMA_MAP:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{req.category}' not found.",
            )

        defaults = await repo.reset_category(req.category)
        await audit_repo.log_audit(
            action_type="SETTINGS_RESET",
            resource_type="app_settings",
            resource_id=req.category,
            outcome="success",
        )
        return {"reset": True, "category": req.category, "defaults": defaults}


@router.get("/{key_or_category}")
async def get_setting_or_category(key_or_category: str, _auth: AuthDep) -> dict[str, Any]:
    """Retrieves either a typed settings category or a raw key value."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)

        if key_or_category in CATEGORY_SCHEMA_MAP:
            cat_data = await repo.get_category(key_or_category)
            return {"category": key_or_category, "value": cat_data}

        val = await repo.get_setting(key_or_category)
        if val is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting or category '{key_or_category}' not found.",
            )
        return {"key": key_or_category, "value": val}


@router.patch("/{key_or_category}")
async def update_setting_or_category(
    key_or_category: str,
    req: dict[str, Any],
    _auth: AuthDep,
) -> dict[str, Any]:
    """Updates a settings category with Pydantic validation, or updates a raw setting key."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        audit_repo = AuditRepository(session)

        if key_or_category in CATEGORY_SCHEMA_MAP:
            # Check if payload is wrapped in 'value' or provided directly
            updates = req.get("value", req) if isinstance(req, dict) else {}
            try:
                updated = await repo.update_category(key_or_category, updates)

                if key_or_category in SENSITIVE_CATEGORIES:
                    await audit_repo.log_audit(
                        action_type="SECURITY_SETTING_UPDATE",
                        resource_type="app_settings",
                        resource_id=key_or_category,
                        outcome="success",
                        metadata={"updated_keys": list(updates.keys())},
                    )

                return {
                    "category": key_or_category,
                    "value": updated,
                    "scope": "system",
                }
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation failed for category '{key_or_category}': {exc}",
                ) from exc

        # Raw key update for backwards compatibility
        val = req.get("value", req)
        scope = req.get("scope", "user") if isinstance(req, dict) else "user"
        setting = await repo.set_setting(key=key_or_category, value=val, scope=scope)
        return {
            "key": setting.key,
            "value": setting.value_json,
            "scope": setting.scope,
            "updated_at": setting.updated_at.isoformat(),
        }


@router.post("/{category}/reset")
async def reset_single_category(category: str, _auth: AuthDep) -> dict[str, Any]:
    """Resets a single settings category to defaults."""
    async with get_db_session() as session:
        repo = SettingsRepository(session)
        audit_repo = AuditRepository(session)

        if category not in CATEGORY_SCHEMA_MAP:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category}' not found.",
            )

        defaults = await repo.reset_category(category)
        await audit_repo.log_audit(
            action_type="SETTINGS_RESET",
            resource_type="app_settings",
            resource_id=category,
            outcome="success",
        )
        return {"reset": True, "category": category, "defaults": defaults}
