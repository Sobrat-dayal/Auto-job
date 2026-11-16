"""Repository for secure credential references and encrypted blob persistence."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CredentialReferenceModel, utc_now
from app.repositories.base import BaseRepository
from app.security.credentials import credential_manager


class CredentialRepository(BaseRepository[CredentialReferenceModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def store_credential(
        self,
        provider: str,
        credential_type: str,
        secret_value: str,
        windows_cred_identifier: str | None = None,
    ) -> CredentialReferenceModel:
        # Encrypt the secret using DPAPI-wrapped vault bound to provider
        encrypted_blob = credential_manager.encrypt_secret(secret_value, provider=provider)

        result = await self.session.execute(
            select(CredentialReferenceModel).where(CredentialReferenceModel.provider == provider)
        )
        cred = result.scalar_one_or_none()

        if cred:
            cred.credential_type = credential_type
            cred.encrypted_blob = encrypted_blob
            cred.windows_cred_identifier = windows_cred_identifier
            cred.status = "active"
            cred.last_validated_at = utc_now()
        else:
            cred = CredentialReferenceModel(
                provider=provider,
                credential_type=credential_type,
                windows_cred_identifier=windows_cred_identifier,
                encrypted_blob=encrypted_blob,
                status="active",
                last_validated_at=utc_now(),
            )
            self.session.add(cred)

        await self.session.flush()
        return cred

    async def get_secret(self, provider: str) -> str | None:
        """Internal authorized retrieval of decrypted secret for automated operations."""
        result = await self.session.execute(
            select(CredentialReferenceModel).where(CredentialReferenceModel.provider == provider)
        )
        cred = result.scalar_one_or_none()
        if not cred:
            return None

        return credential_manager.decrypt_secret(cred.encrypted_blob, provider=provider)

    async def list_credential_status(self) -> list[dict[str, Any]]:
        """Safe non-sensitive listing of configured providers for UI and health diagnostics."""
        result = await self.session.execute(select(CredentialReferenceModel))
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "provider": r.provider,
                "credential_type": r.credential_type,
                "status": r.status,
                "is_configured": True,
                "created_at": r.created_at.isoformat(),
                "last_validated_at": r.last_validated_at.isoformat() if r.last_validated_at else None,
            }
            for r in records
        ]

    async def delete_credential(self, provider: str) -> bool:
        result = await self.session.execute(
            select(CredentialReferenceModel).where(CredentialReferenceModel.provider == provider)
        )
        cred = result.scalar_one_or_none()
        if not cred:
            return False

        await self.session.delete(cred)
        await self.session.flush()
        return True
