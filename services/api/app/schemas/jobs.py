"""Pydantic schemas for Job Listings and Discovery."""

from datetime import datetime

from pydantic import BaseModel, Field


class JobListingResponse(BaseModel):
    id: str = Field(description="Unique job listing identifier")
    source_id: str = Field(description="Foreign key to originating JobSource")
    external_id: str = Field(description="External job posting identifier from board/ATS")
    company: str = Field(description="Company offering the position")
    title: str = Field(description="Job title")
    location: str | None = Field(default=None, description="Geographic location or remote status")
    employment_type: str | None = Field(default=None, description="Full-time, part-time, contract, etc.")
    work_arrangement: str | None = Field(default=None, description="remote, hybrid, onsite")
    salary_range: str | None = Field(default=None, description="Disclosed salary range")
    description: str | None = Field(default=None, description="Full job description")
    requirements: str | None = Field(default=None, description="Parsed requirement notes")
    application_url: str = Field(description="Direct URL to job posting or application portal")
    discovered_at: datetime = Field(description="Timestamp when listing was first recorded")
    last_verified_at: datetime | None = Field(default=None, description="Last verification check")
    status: str = Field(default="active", description="active, expired, closed, hidden")


class JobListResponse(BaseModel):
    items: list[JobListingResponse]
    total: int = Field(ge=0, description="Total matching listings count")
    limit: int = Field(ge=1, description="Page size limit")
    offset: int = Field(ge=0, description="Page offset")
