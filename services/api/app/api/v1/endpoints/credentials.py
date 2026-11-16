"""Secure credential management and integration status endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import CredentialRepository

router = APIRouter(prefix="/integrations/credentials", tags=["credentials"])


class CredentialStoreRequest(BaseModel):
    provider: str = Field(description="Service or model provider name (e.g., anthropic, openai, gemini)")
    credential_type: str = Field(default="api_key", description="Type of credential: api_key, oauth_token, mcp_secret")
    secret_value: str = Field(description="Raw secret value to be encrypted at rest with Windows DPAPI")


@router.get("/status")
async def list_credential_status(_auth: AuthDep) -> list[dict[str, Any]]:
    """Returns availability status of configured credential providers without exposing secret values."""
    async with get_db_session() as session:
        repo = CredentialRepository(session)
        return await repo.list_credential_status()


@router.post("", status_code=status.HTTP_201_CREATED)
async def store_credential(req: CredentialStoreRequest, _auth: AuthDep) -> dict[str, Any]:
    """Stores a credential encrypted at rest using Windows DPAPI key wrapping."""
    async with get_db_session() as session:
        repo = CredentialRepository(session)
        cred = await repo.store_credential(
            provider=req.provider,
            credential_type=req.credential_type,
            secret_value=req.secret_value,
        )
        return {
            "provider": cred.provider,
            "credential_type": cred.credential_type,
            "status": cred.status,
            "is_configured": True,
            "created_at": cred.created_at.isoformat(),
        }


@router.delete("/{provider}")
async def delete_credential(provider: str, _auth: AuthDep) -> dict[str, Any]:
    """Deletes and revokes a configured credential."""
    async with get_db_session() as session:
        repo = CredentialRepository(session)
        deleted = await repo.delete_credential(provider)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential for provider '{provider}' not found.",
            )
        return {"deleted": True, "provider": provider}
