"""Integration configuration and status endpoints."""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import CredentialRepository, SettingsRepository

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/configurations")
async def list_integration_configurations(_auth: AuthDep) -> dict[str, Any]:
    """Returns safe configuration metadata for external services, MCP servers, and credentials."""
    async with get_db_session() as session:
        cred_repo = CredentialRepository(session)
        settings_repo = SettingsRepository(session)

        cred_statuses = await cred_repo.list_credential_status()
        integration_settings = await settings_repo.get_category("integrations")

        return {
            "credentials": cred_statuses,
            "mcp_servers": integration_settings.get("mcp_servers", []),
            "services": {
                "email": integration_settings.get("email_integration_enabled", False),
                "telegram": integration_settings.get("telegram_integration_enabled", False),
                "whatsapp": integration_settings.get("whatsapp_integration_enabled", False),
                "job_boards": integration_settings.get("job_board_scouting_enabled", True),
            },
        }
