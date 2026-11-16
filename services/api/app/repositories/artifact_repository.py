"""Repository for artifact metadata storage and path validation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ArtifactModel
from app.repositories.base import BaseRepository


class ArtifactRepository(BaseRepository[ArtifactModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_artifact(
        self,
        artifact_type: str,
        storage_path: str,
        file_size: int,
        checksum: str,
        related_task_id: str | None = None,
        related_profile_id: str | None = None,
        related_application_id: str | None = None,
        retention_class: str = "permanent",
    ) -> ArtifactModel:
        artifact = ArtifactModel(
            artifact_type=artifact_type,
            storage_path=storage_path,
            file_size=file_size,
            checksum=checksum,
            related_task_id=related_task_id,
            related_profile_id=related_profile_id,
            related_application_id=related_application_id,
            retention_class=retention_class,
        )
        self.session.add(artifact)
        await self.session.flush()
        return artifact

    async def get_artifact(self, artifact_id: str) -> ArtifactModel | None:
        result = await self.session.execute(select(ArtifactModel).where(ArtifactModel.id == artifact_id))
        return result.scalar_one_or_none()
