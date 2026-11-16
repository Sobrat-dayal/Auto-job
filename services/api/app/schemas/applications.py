"""Pydantic schemas for Job Applications and Execution Attempts."""

from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationAttemptResponse(BaseModel):
    id: str = Field(description="Unique attempt identifier")
    application_id: str = Field(description="Parent application ID")
    attempted_at: datetime = Field(description="Execution timestamp")
    execution_status: str = Field(description="pending, submitted, failed, interrupted")
    failure_category: str | None = Field(default=None, description="Categorized failure reason")
    error_summary: str | None = Field(default=None, description="Diagnostic error summary")
    retry_eligible: bool = Field(default=False, description="Whether retry is permitted under policy")
    idempotency_key: str = Field(description="Unique idempotency token preventing duplicate submissions")


class ApplicationResponse(BaseModel):
    id: str = Field(description="Unique application identifier")
    job_id: str = Field(description="Target job listing identifier")
    profile_id: str = Field(description="Applicant profile identifier")
    resume_version_id: str | None = Field(default=None, description="Associated tailored resume version")
    status: str = Field(default="draft", description="draft, ready, submitted, rejected, interviewing, offered")
    submitted_at: datetime | None = Field(default=None, description="Submission timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    confirmation_ref: str | None = Field(default=None, description="Portal confirmation or tracking number")
    notes: str | None = Field(default=None, description="User or agent execution notes")
    authorization_ref: str | None = Field(default=None, description="Human authorization signature or token")
    company: str | None = Field(default=None, description="Target company name (enriched)")
    job_title: str | None = Field(default=None, description="Target job title (enriched)")
    attempts: list[ApplicationAttemptResponse] = Field(
        default_factory=list, description="Historical execution attempts"
    )


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int = Field(ge=0, description="Total matching applications count")
    limit: int = Field(ge=1, description="Page size limit")
    offset: int = Field(ge=0, description="Page offset")
