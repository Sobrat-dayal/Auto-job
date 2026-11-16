"""Artifacts and Document metadata REST API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories import ArtifactRepository
from app.schemas.artifacts import ArtifactListResponse, ArtifactResponse

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("", response_model=ArtifactListResponse)
async def list_artifacts(
    _auth: AuthDep,
    artifact_type: Annotated[str | None, Query(description="Filter by artifact type")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Max artifacts to return")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> ArtifactListResponse:
    """Lists persistent artifacts and documents stored in SQLite."""
    async with get_db_session() as session:
        repo = ArtifactRepository(session)
        items = await repo.list_artifacts(artifact_type=artifact_type, limit=limit, offset=offset)
        total = await repo.count_artifacts(artifact_type=artifact_type)

    return ArtifactListResponse(
        items=[
            ArtifactResponse(
                id=a.id,
                artifact_type=a.artifact_type,
                storage_path=a.storage_path,
                file_size=a.file_size,
                checksum=a.checksum,
                related_task_id=a.related_task_id,
                related_profile_id=a.related_profile_id,
                related_application_id=a.related_application_id,
                retention_class=a.retention_class,
                created_at=a.created_at,
            )
            for a in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: str,
    _auth: AuthDep,
) -> ArtifactResponse:
    """Retrieves metadata of a specific persistent artifact."""
    async with get_db_session() as session:
        repo = ArtifactRepository(session)
        a = await repo.get_artifact(artifact_id)
        if not a:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact '{artifact_id}' not found",
            )

    return ArtifactResponse(
        id=a.id,
        artifact_type=a.artifact_type,
        storage_path=a.storage_path,
        file_size=a.file_size,
        checksum=a.checksum,
        related_task_id=a.related_task_id,
        related_profile_id=a.related_profile_id,
        related_application_id=a.related_application_id,
        retention_class=a.retention_class,
        created_at=a.created_at,
    )
