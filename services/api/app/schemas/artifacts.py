"""Pydantic schemas for Artifacts and Documents metadata."""

from datetime import datetime

from pydantic import BaseModel, Field


class ArtifactResponse(BaseModel):
    id: str = Field(description="Unique artifact identifier")
    artifact_type: str = Field(description="resume_pdf, report, document, spreadsheet, presentation, 3d_model, render")
    storage_path: str = Field(description="Relative path inside the secure application storage")
    file_size: int = Field(ge=0, description="File size in bytes")
    checksum: str = Field(description="SHA-256 integrity checksum")
    related_task_id: str | None = Field(default=None, description="Originating task ID")
    related_profile_id: str | None = Field(default=None, description="Related profile ID")
    related_application_id: str | None = Field(default=None, description="Related application ID")
    retention_class: str = Field(default="permanent", description="permanent, temporary, cache")
    created_at: datetime = Field(description="Timestamp when artifact was persisted")


class ArtifactListResponse(BaseModel):
    items: list[ArtifactResponse]
    total: int = Field(ge=0, description="Total matching artifacts count")
    limit: int = Field(ge=1, description="Page size limit")
    offset: int = Field(ge=0, description="Page offset")
