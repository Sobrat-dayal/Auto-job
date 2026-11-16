"""Storage diagnostics, integrity verification, online backups, and restoration endpoints."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.core.config import settings
from app.db.backup import create_database_backup, list_backups, restore_database_backup
from app.db.maintenance import get_storage_status, verify_database_integrity

router = APIRouter(prefix="/storage", tags=["storage"])


class RestoreRequest(BaseModel):
    filename: str = Field(description="Filename of the backup .db file to restore from")
    confirm: bool = Field(description="Explicit user confirmation for database restoration")


@router.get("/status")
async def storage_status(_auth: AuthDep) -> dict[str, Any]:
    """Returns database sizes, WAL size, artifact storage, and backup summary."""
    return await get_storage_status()


@router.get("/health")
async def storage_health(_auth: AuthDep) -> dict[str, Any]:
    """Runs PRAGMA integrity_check and PRAGMA foreign_key_check without exposing internal filesystem paths."""
    return await verify_database_integrity()


@router.post("/backups", status_code=status.HTTP_201_CREATED)
async def trigger_backup(_auth: AuthDep) -> dict[str, Any]:
    """Creates an online consistent backup snapshot and returns the backup manifest."""
    try:
        manifest = await create_database_backup()
        return manifest
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup creation failed: {exc}",
        ) from exc


@router.get("/backups")
async def list_available_backups(_auth: AuthDep) -> list[dict[str, Any]]:
    """Returns all available database backups and their metadata manifests, newest first."""
    return list_backups()


@router.post("/restore")
async def restore_backup(req: RestoreRequest, _auth: AuthDep) -> dict[str, Any]:
    """Restores database from an authorized, verified backup snapshot."""
    if not req.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restoration requires explicit confirmation: confirm=true.",
        )

    # Path traversal protection: ensure filename has no directory separators
    clean_filename = Path(req.filename).name
    backup_file = settings.backups_dir / clean_filename

    if not backup_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup file '{clean_filename}' was not found in backups directory.",
        )

    try:
        result = await restore_database_backup(backup_file)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Restoration failed: {exc}",
        ) from exc
