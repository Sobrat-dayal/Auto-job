"""SQLAlchemy 2.x declarative ORM models for AUTONOM persistent storage."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# A. Application Settings
# ---------------------------------------------------------------------------
class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    scope: Mapped[str] = mapped_column(String(64), default="system", nullable=False)


# ---------------------------------------------------------------------------
# B. Applicant Profiles & Portfolio Records
# ---------------------------------------------------------------------------
class ApplicantProfile(Base):
    __tablename__ = "applicant_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_name: Mapped[str] = mapped_column(String(128), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_info_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    education_json: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, default=list)
    experience_json: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, default=list)
    career_preferences_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    skills: Mapped[list["VerifiedSkill"]] = relationship(
        "VerifiedSkill", back_populates="profile", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["ProfileEvidence"]] = relationship(
        "ProfileEvidence", back_populates="profile", cascade="all, delete-orphan"
    )
    resumes: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion", back_populates="profile", cascade="all, delete-orphan"
    )


class VerifiedSkill(Base):
    __tablename__ = "verified_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), default="technical", nullable=False)
    evidence_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    profile: Mapped["ApplicantProfile"] = relationship("ApplicantProfile", back_populates="skills")


class ProfileEvidence(Base):
    __tablename__ = "profile_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)  # github_commit, diploma, cert, doc
    project_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="verified", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    profile: Mapped["ApplicantProfile"] = relationship("ApplicantProfile", back_populates="evidence")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_tag: Mapped[str] = mapped_column(String(64), nullable=False)
    template_id: Mapped[str] = mapped_column(String(64), default="standard_ats", nullable=False)
    artifact_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)

    profile: Mapped["ApplicantProfile"] = relationship("ApplicantProfile", back_populates="resumes")


# ---------------------------------------------------------------------------
# C. Job Sources, Listings, Matches & Applications
# ---------------------------------------------------------------------------
class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    platform_name: Mapped[str] = mapped_column(String(64), nullable=False)  # linkedin, greenhouse, lever, indeed
    source_type: Mapped[str] = mapped_column(String(32), default="web", nullable=False)
    source_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    connector_config_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_status: Mapped[str | None] = mapped_column(String(256), nullable=True)

    listings: Mapped[list["JobListing"]] = relationship(
        "JobListing", back_populates="source", cascade="all, delete-orphan"
    )


class JobListing(Base):
    __tablename__ = "job_listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    company: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    work_arrangement: Mapped[str | None] = mapped_column(String(32), nullable=True)  # remote, hybrid, onsite
    salary_range: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str] = mapped_column(String(512), nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, index=True)

    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_job_listings_source_external_id"),)

    source: Mapped["JobSource"] = relationship("JobSource", back_populates="listings")
    matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan"
    )


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, index=True)  # 0.0 - 1.0
    matching_factors_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    missing_requirements_json: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    eligibility_status: Mapped[str] = mapped_column(String(32), default="eligible", nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    evaluator_version: Mapped[str] = mapped_column(String(32), default="v1.0", nullable=False)

    job: Mapped["JobListing"] = relationship("JobListing", back_populates="matches")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applicant_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_version_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(32), default="draft", nullable=False, index=True
    )  # draft, ready, submitted, rejected, interviewing, offered
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    confirmation_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    authorization_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)

    job: Mapped["JobListing"] = relationship("JobListing", back_populates="applications")
    attempts: Mapped[list["ApplicationAttempt"]] = relationship(
        "ApplicationAttempt", back_populates="application", cascade="all, delete-orphan"
    )


class ApplicationAttempt(Base):
    __tablename__ = "application_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    execution_status: Mapped[str] = mapped_column(String(32), nullable=False)  # pending, submitted, failed, interrupted
    failure_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmation_evidence_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    retry_eligible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    application: Mapped["Application"] = relationship("Application", back_populates="attempts")


# ---------------------------------------------------------------------------
# D. Persistent Tasks, Task Events & Worker Runs
# ---------------------------------------------------------------------------
class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), default="normal", nullable=False)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    progress_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    input_payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    output_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    owner_context: Mapped[str | None] = mapped_column(String(64), default="user", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    timeout_seconds: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    error_info_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    events: Mapped[list["TaskEventModel"]] = relationship(
        "TaskEventModel", back_populates="task", cascade="all, delete-orphan"
    )
    worker_runs: Mapped[list["WorkerRunModel"]] = relationship(
        "WorkerRunModel", back_populates="task", cascade="all, delete-orphan"
    )


class TaskEventModel(Base):
    __tablename__ = "task_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    state_transition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sequence_num: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="events")


class WorkerRunModel(Base):
    __tablename__ = "worker_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    worker_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    execution_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    failure_class: Mapped[str | None] = mapped_column(String(128), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="worker_runs")


# ---------------------------------------------------------------------------
# E. Agent Definitions & Metadata
# ---------------------------------------------------------------------------
class AgentDefinitionModel(Base):
    __tablename__ = "agent_definitions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(128), nullable=False)
    capabilities_json: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    config_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


# ---------------------------------------------------------------------------
# F. Artifacts & Credential References
# ---------------------------------------------------------------------------
class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # resume_pdf, report, document
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    related_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    related_profile_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    related_application_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    retention_class: Mapped[str] = mapped_column(String(32), default="permanent", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class CredentialReferenceModel(Base):
    __tablename__ = "credential_references"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    provider: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    credential_type: Mapped[str] = mapped_column(String(32), default="api_key", nullable=False)
    windows_cred_identifier: Mapped[str | None] = mapped_column(String(128), nullable=True)
    encrypted_blob: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# G. Security Audit Events
# ---------------------------------------------------------------------------
class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    actor_id: Mapped[str] = mapped_column(String(64), default="user", nullable=False)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    outcome: Mapped[str] = mapped_column(String(32), default="success", nullable=False)  # success, denied, failed
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    safe_metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)


# ---------------------------------------------------------------------------
# H. AI Model Registry, Inference Requests & Routing Preferences (Stage 11)
# ---------------------------------------------------------------------------
class AIModelRecord(Base):
    __tablename__ = "ai_models"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)  # provider_id:model_id
    provider_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(32), default="local", nullable=False)  # local or cloud
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    context_window: Mapped[int] = mapped_column(Integer, default=8192, nullable=False)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)
    capabilities_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pricing_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    reported_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantization: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_discovered_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    last_invoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class AIInferenceRequestRecord(Base):
    __tablename__ = "ai_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    task_category: Mapped[str] = mapped_column(String(64), default="general_conversation", nullable=False, index=True)
    provider_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    routing_strategy: Mapped[str] = mapped_column(String(32), default="local_first", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False, index=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_source: Mapped[str] = mapped_column(String(32), default="reported", nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    time_to_first_token_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    routing_decision_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    prompt_preview: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AIRoutingPreferenceRecord(Base):
    __tablename__ = "ai_routing_preferences"

    category: Mapped[str] = mapped_column(String(64), primary_key=True)
    preferred_provider: Mapped[str] = mapped_column(String(64), default="ollama", nullable=False)
    preferred_model: Mapped[str] = mapped_column(String(128), default="llama3.1:8b", nullable=False)
    fallback_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fallback_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_local_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


# ---------------------------------------------------------------------------
# S. Multi-Agent Orchestration Models (Stage 12)
# ---------------------------------------------------------------------------

class WorkflowRecord(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="created", nullable=False, index=True)
    active_plan_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    priority: Mapped[str] = mapped_column(String(32), default="normal", nullable=False)
    context_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    constraints_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    failed_steps: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    plans: Mapped[list["WorkflowPlanRecord"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")
    steps: Mapped[list["WorkflowStepRecord"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class WorkflowPlanRecord(Base):
    __tablename__ = "workflow_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    plan_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    success_criteria_json: Mapped[list[Any]] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    workflow: Mapped["WorkflowRecord"] = relationship(back_populates="plans")
    steps: Mapped[list["WorkflowStepRecord"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class WorkflowStepRecord(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflow_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    capability_id: Mapped[str] = mapped_column(String(64), nullable=False)
    assigned_agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    input_bindings_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_info_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    verification_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    verification_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=2)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    workflow: Mapped["WorkflowRecord"] = relationship(back_populates="steps")
    plan: Mapped["WorkflowPlanRecord"] = relationship(back_populates="steps")

    __table_args__ = (
        UniqueConstraint("workflow_id", "plan_id", "step_id", name="uq_workflow_plan_step"),
    )


class WorkflowDependencyRecord(Base):
    __tablename__ = "workflow_dependencies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    depends_on_step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class AgentExecutionRecord(Base):
    __tablename__ = "agent_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AgentMessageRecord(Base):
    __tablename__ = "agent_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    recipient_agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)


class VerificationResultRecord(Base):
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    verification_type: Mapped[str] = mapped_column(String(32), default="deterministic", nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class RecoveryAttemptRecord(Base):
    __tablename__ = "recovery_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    failure_category: Mapped[str] = mapped_column(String(64), nullable=False)
    recovery_action: Mapped[str] = mapped_column(String(64), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

