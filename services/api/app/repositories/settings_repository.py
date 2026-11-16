"""Repository for application settings persistence."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppSetting
from app.repositories.base import BaseRepository


class SettingsRepository(BaseRepository[AppSetting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

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
