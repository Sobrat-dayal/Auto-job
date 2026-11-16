"""Repository for centralized application settings persistence, validation, and metadata."""

from typing import Any

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppSetting, utc_now
from app.repositories.base import BaseRepository
from app.schemas.settings import (
    AgentSettings,
    AISettings,
    AllSettingsResponse,
    AppearanceSettings,
    AutomationSettings,
    ComputerControlSettings,
    DesktopSettings,
    GeneralSettings,
    IntegrationSettings,
    NotificationSettings,
    PermissionSettings,
    RecruitmentSettings,
    SecurityPrivacySettings,
    SettingItemMetadata,
    SettingsSchemaMetadataResponse,
    StorageSettings,
)

CATEGORY_SCHEMA_MAP: dict[str, type] = {
    "general": GeneralSettings,
    "appearance": AppearanceSettings,
    "ai": AISettings,
    "agents": AgentSettings,
    "automation": AutomationSettings,
    "permissions": PermissionSettings,
    "computer": ComputerControlSettings,
    "integrations": IntegrationSettings,
    "recruitment": RecruitmentSettings,
    "storage": StorageSettings,
    "notifications": NotificationSettings,
    "desktop": DesktopSettings,
    "security": SecurityPrivacySettings,
}


class SettingsRepository(BaseRepository[AppSetting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    # --------------------------------------------------------------------------
    # Backward compatible raw key-value methods
    # --------------------------------------------------------------------------
    async def get_setting(self, key: str) -> dict[str, Any] | None:
        result = await self.session.execute(select(AppSetting).where(AppSetting.key == key))
        setting = result.scalar_one_or_none()
        return setting.value_json if setting else None

    async def set_setting(self, key: str, value: dict[str, Any], scope: str = "system") -> AppSetting:
        result = await self.session.execute(select(AppSetting).where(AppSetting.key == key))
        setting = result.scalar_one_or_none()

        if setting:
            setting.value_json = value
            setting.scope = scope
            setting.updated_at = utc_now()
        else:
            setting = AppSetting(key=key, value_json=value, scope=scope)
            self.session.add(setting)

        await self.session.flush()
        return setting

    async def list_settings(self, scope: str | None = None) -> list[AppSetting]:
        query = select(AppSetting)
        if scope:
            query = query.where(AppSetting.scope == scope)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # Category-level methods
    # --------------------------------------------------------------------------
    async def get_category(self, category: str) -> dict[str, Any]:
        """Retrieves category settings merged with schema defaults."""
        if category not in CATEGORY_SCHEMA_MAP:
            raise KeyError(f"Unknown settings category '{category}'. Valid: {list(CATEGORY_SCHEMA_MAP.keys())}")

        schema_cls = CATEGORY_SCHEMA_MAP[category]
        default_inst = schema_cls()
        default_dict = default_inst.model_dump()

        raw = await self.get_setting(f"settings:{category}")
        if not raw:
            return default_dict

        # Merge stored values with default dict to ensure new schema fields exist
        merged = {**default_dict, **raw}
        # Validate through schema
        validated = schema_cls(**merged)
        return validated.model_dump()

    async def update_category(self, category: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Applies partial updates to a settings category, validates with Pydantic, and persists."""
        if category not in CATEGORY_SCHEMA_MAP:
            raise KeyError(f"Unknown settings category '{category}'. Valid: {list(CATEGORY_SCHEMA_MAP.keys())}")

        current = await self.get_category(category)
        merged = {**current, **updates}

        schema_cls = CATEGORY_SCHEMA_MAP[category]
        validated = schema_cls(**merged)
        validated_dict = validated.model_dump()

        await self.set_setting(f"settings:{category}", validated_dict, scope="system")
        return validated_dict

    async def reset_category(self, category: str) -> dict[str, Any]:
        """Resets a settings category to default values."""
        if category not in CATEGORY_SCHEMA_MAP:
            raise KeyError(f"Unknown settings category '{category}'. Valid: {list(CATEGORY_SCHEMA_MAP.keys())}")

        schema_cls = CATEGORY_SCHEMA_MAP[category]
        defaults = schema_cls().model_dump()
        await self.set_setting(f"settings:{category}", defaults, scope="system")
        return defaults

    async def get_all_settings(self) -> AllSettingsResponse:
        """Retrieves aggregated settings across all 13 categories."""
        general = await self.get_category("general")
        appearance = await self.get_category("appearance")
        ai = await self.get_category("ai")
        agents = await self.get_category("agents")
        automation = await self.get_category("automation")
        permissions = await self.get_category("permissions")
        computer = await self.get_category("computer")
        integrations = await self.get_category("integrations")
        recruitment = await self.get_category("recruitment")
        storage = await self.get_category("storage")
        notifications = await self.get_category("notifications")
        desktop = await self.get_category("desktop")
        security = await self.get_category("security")

        # Get latest updated_at
        result = await self.session.execute(
            select(AppSetting.updated_at).order_by(AppSetting.updated_at.desc()).limit(1)
        )
        latest_ts = result.scalar_one_or_none()
        ts_str = latest_ts.isoformat() if latest_ts else None

        return AllSettingsResponse(
            general=GeneralSettings(**general),
            appearance=AppearanceSettings(**appearance),
            ai=AISettings(**ai),
            agents=AgentSettings(**agents),
            automation=AutomationSettings(**automation),
            permissions=PermissionSettings(**permissions),
            computer=ComputerControlSettings(**computer),
            integrations=IntegrationSettings(**integrations),
            recruitment=RecruitmentSettings(**recruitment),
            storage=StorageSettings(**storage),
            notifications=NotificationSettings(**notifications),
            desktop=DesktopSettings(**desktop),
            security=SecurityPrivacySettings(**security),
            version=1,
            last_updated_at=ts_str,
        )

    async def export_settings(self, app_version: str = "0.1.0") -> dict[str, Any]:
        """Exports all non-sensitive configuration categories into a portable payload."""
        all_settings = await self.get_all_settings()
        exported = {
            "app_version": app_version,
            "exported_at": utc_now().isoformat(),
            "schema_version": 1,
            "settings": {
                "general": all_settings.general.model_dump(),
                "appearance": all_settings.appearance.model_dump(),
                "ai": all_settings.ai.model_dump(),
                "agents": all_settings.agents.model_dump(),
                "automation": all_settings.automation.model_dump(),
                "permissions": all_settings.permissions.model_dump(),
                "computer": all_settings.computer.model_dump(),
                "integrations": all_settings.integrations.model_dump(),
                "recruitment": all_settings.recruitment.model_dump(),
                "storage": all_settings.storage.model_dump(),
                "notifications": all_settings.notifications.model_dump(),
                "desktop": all_settings.desktop.model_dump(),
                "security": all_settings.security.model_dump(),
            },
        }
        return exported

    async def import_settings(self, import_data: dict[str, Any]) -> dict[str, Any]:
        """Validates and imports non-sensitive settings, rejecting malformed or unknown structures."""
        if not isinstance(import_data, dict):
            raise ValueError("Import payload must be a JSON object")

        settings_dict = import_data.get("settings", {})
        if not isinstance(settings_dict, dict):
            raise ValueError("Import payload missing 'settings' object")

        imported_categories: list[str] = []
        for cat, values in settings_dict.items():
            if cat in CATEGORY_SCHEMA_MAP and isinstance(values, dict):
                # Validate with category schema
                schema_cls = CATEGORY_SCHEMA_MAP[cat]
                try:
                    validated = schema_cls(**values)
                    await self.set_setting(f"settings:{cat}", validated.model_dump(), scope="system")
                    imported_categories.append(cat)
                except ValidationError as exc:
                    raise ValueError(f"Validation failed for category '{cat}': {exc}") from exc

        return {
            "success": True,
            "imported_categories": imported_categories,
            "total_categories": len(imported_categories),
        }

    def get_schema_metadata(self) -> SettingsSchemaMetadataResponse:
        """Returns metadata for settings items, categories, defaults, and requirements."""
        items: list[SettingItemMetadata] = []
        for cat_name, schema_cls in CATEGORY_SCHEMA_MAP.items():
            inst = schema_cls()
            fields = schema_cls.model_fields
            for field_name, field_info in fields.items():
                val = getattr(inst, field_name)
                # Determine if restart required (e.g. backend workers, port, etc.)
                requires_restart = field_name in (
                    "max_concurrent_workers",
                    "max_queued_tasks",
                    "auto_start_backend_sidecar",
                    "single_active_model_enforced",
                )
                items.append(
                    SettingItemMetadata(
                        key=f"{cat_name}.{field_name}",
                        category=cat_name,
                        setting_type=str(field_info.annotation),
                        default_value=val,
                        description=field_info.description or field_name,
                        requires_restart=requires_restart,
                        is_sensitive=False,
                        availability="available",
                    )
                )

        return SettingsSchemaMetadataResponse(
            schema_version=1,
            categories=list(CATEGORY_SCHEMA_MAP.keys()),
            items=items,
        )
