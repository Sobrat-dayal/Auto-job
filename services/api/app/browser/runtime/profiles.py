"""Profile management service for persistent browser identities and session states."""

from datetime import datetime, timezone
import logging
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.contracts import BrowserProfileCreateRequest, BrowserProfileResponse
from app.browser.security.authentication import BrowserAuthenticationManager
from app.db.models import BrowserProfileRecord

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BrowserProfileService:
    """Manages browser profiles with domain scopes and authenticated storage states."""

    def __init__(self, auth_manager: BrowserAuthenticationManager | None = None) -> None:
        self.auth_manager = auth_manager or BrowserAuthenticationManager()

    async def create_profile(
        self, session: AsyncSession, req: BrowserProfileCreateRequest
    ) -> BrowserProfileResponse:
        """Creates a new browser profile record."""
        profile_id = str(uuid4())
        storage_path = str(self.auth_manager.get_profile_state_path(profile_id))

        record = BrowserProfileRecord(
            id=profile_id,
            name=req.name,
            description=req.description,
            storage_path=storage_path,
            is_authenticated=False,
            domain_scopes_json=req.domain_scopes,
            last_used_at=None,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)

        return self._to_response(record)

    async def list_profiles(self, session: AsyncSession) -> list[BrowserProfileResponse]:
        """Lists all browser profiles."""
        stmt = select(BrowserProfileRecord).order_by(BrowserProfileRecord.created_at.desc())
        res = await session.execute(stmt)
        records = res.scalars().all()
        return [self._to_response(r) for r in records]

    async def get_profile(
        self, session: AsyncSession, profile_id: str
    ) -> BrowserProfileRecord | None:
        """Retrieves a single browser profile record."""
        stmt = select(BrowserProfileRecord).where(BrowserProfileRecord.id == profile_id)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def mark_profile_authenticated(
        self, session: AsyncSession, profile_id: str, state_data: dict
    ) -> bool:
        """Saves encrypted storage state and flags the profile as authenticated."""
        record = await self.get_profile(session, profile_id)
        if not record:
            return False

        self.auth_manager.save_storage_state(profile_id, state_data)
        record.is_authenticated = True
        record.last_used_at = utc_now()
        record.updated_at = utc_now()
        await session.commit()
        return True

    def _to_response(self, record: BrowserProfileRecord) -> BrowserProfileResponse:
        return BrowserProfileResponse(
            id=record.id,
            name=record.name,
            description=record.description,
            storage_path=record.storage_path,
            is_authenticated=record.is_authenticated,
            domain_scopes=record.domain_scopes_json or [],
            last_used_at=record.last_used_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
