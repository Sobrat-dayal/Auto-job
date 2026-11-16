"""Base repository and common query utilities."""

from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base repository encapsulating an active AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
