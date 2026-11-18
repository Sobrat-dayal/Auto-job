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


class AgentConfigurationRecord(Base):
    __tablename__ = "agent_configurations"

    agent_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    concurrency_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048, nullable=False)
    local_first: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cloud_permitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_capabilities_json: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    custom_settings_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


# ---------------------------------------------------------------------------
# K. Stage 14: Central Authorization, Policies, Grants & Approvals
# ---------------------------------------------------------------------------
class AuthorizationPolicyRecord(Base):
    __tablename__ = "authorization_policies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    subject_scope: Mapped[str] = mapped_column(String(128), default="*", nullable=False)  # agent_id, role:*, or *
    category_scope: Mapped[str] = mapped_column(String(64), default="*", nullable=False)
    action_scope_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    resource_scope_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    effect: Mapped[str] = mapped_column(String(32), default="allow", nullable=False)  # allow, deny, require_approval
    conditions_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class AuthorizationPolicyVersionRecord(Base):
    __tablename__ = "authorization_policy_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("authorization_policies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    modified_by: Mapped[str] = mapped_column(String(64), default="user", nullable=False)
    change_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class AuthorizationGrantRecord(Base):
    __tablename__ = "authorization_grants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    grant_type: Mapped[str] = mapped_column(String(32), default="standing", nullable=False)  # standing, workflow_scoped, task_scoped, time_limited, one_time
    subject_type: Mapped[str] = mapped_column(String(32), default="agent", nullable=False)  # user, agent, workflow
    subject_id: Mapped[str] = mapped_column(String(128), default="*", nullable=False)
    workflow_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    allowed_capabilities_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    resource_scope_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    risk_limit: Mapped[str] = mapped_column(String(32), default="moderate", nullable=False)  # low, moderate, high, critical
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    use_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_by: Mapped[str] = mapped_column(String(64), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class ApprovalRequestRecord(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    capability_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    resource_scope_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    parameters_digest: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 hash of parameters
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), default="moderate", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending, approved, denied, expired, cancelled, revoked, consumed
    approval_mode: Mapped[str] = mapped_column(String(32), default="one_time", nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuthorizationDecisionRecord(Base):
    __tablename__ = "authorization_decisions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    workflow_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    capability_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)  # allow, deny, require_approval
    policy_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    grant_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason_code: Mapped[str] = mapped_column(String(64), default="POLICY_EVALUATED", nullable=False)
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)


class EmergencyStopStateRecord(Base):
    __tablename__ = "emergency_stop_state"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default="global_state")
    is_emergency_stop_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    emergency_stop_activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    emergency_stop_activated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    emergency_stop_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_automation_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    automation_paused_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    automation_paused_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    automation_pause_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


# ---------------------------------------------------------------------------
# Stage 15: Persistent Agent Memory & Hybrid Retrieval Engine
# ---------------------------------------------------------------------------
class MemoryRecord(Base):
    __tablename__ = "memory_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    memory_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # working, episodic, semantic, procedural
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    owner_scope: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # user, applicant_profile, workflow, task, agent, project, integration, shared
    scope_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)  # user_statement, verified_profile, document, task_execution, tool_output, external_source, ai_synthesis
    source_ref: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    provenance_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified", nullable=False, index=True)  # verified, user_confirmed, evidence_supported, unverified, conflicted, superseded, expired, rejected
    confidence_category: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)  # high, medium, low, unrated
    sensitivity_category: Mapped[str] = mapped_column(String(32), default="internal", nullable=False, index=True)  # public, internal, personal, sensitive, restricted, secret
    visibility_policy: Mapped[str] = mapped_column(String(32), default="scoped", nullable=False)  # scoped, shared, private
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    superseded_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    embedding_model_id: Mapped[str] = mapped_column(String(64), default="local-minilm-l6", nullable=False)
    embedding_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    embedding_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending, completed, failed, not_required
    content_checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # sha256
    retention_policy: Mapped[str] = mapped_column(String(32), default="permanent", nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class MemoryEmbeddingRecord(Base):
    __tablename__ = "memory_embeddings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    memory_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding_model_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_json: Mapped[list[float]] = mapped_column(JSON, nullable=False)  # JSON-encoded array of float embeddings
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class MemoryConflictRecord(Base):
    __tablename__ = "memory_conflicts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    memory_id_a: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    memory_id_b: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    conflict_type: Mapped[str] = mapped_column(String(64), default="contradiction", nullable=False)  # contradiction, outdated_preference, scope_mismatch
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="unresolved", nullable=False, index=True)  # unresolved, resolved, dismissed
    resolution_action: Mapped[str | None] = mapped_column(String(64), nullable=True)  # supersede, keep_both, edit, reject
    resolved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ProceduralMemoryRecord(Base):
    __tablename__ = "procedural_memories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    procedure_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    capability_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    required_inputs_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    steps_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    preconditions_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    expected_outputs_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_requirements_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    required_permissions_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    provenance_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    validation_status: Mapped[str] = mapped_column(String(32), default="candidate", nullable=False, index=True)  # candidate, validated, deprecated, rejected
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class MemoryAccessEventRecord(Base):
    __tablename__ = "memory_access_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    memory_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    actor_id: Mapped[str] = mapped_column(String(64), default="user", nullable=False)
    agent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    workflow_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)  # read, search, create, update, delete, export, consolidate
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)  # allowed, denied
    reason: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Stage 16: Browser Automation Models
# ---------------------------------------------------------------------------
class BrowserSessionRecord(Base):
    __tablename__ = "browser_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    browser_type: Mapped[str] = mapped_column(String(32), default="chromium", nullable=False)
    channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="created", nullable=False, index=True)  # created, launching, running, paused, error, closed
    is_headless: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    active_tab_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    viewport_width: Mapped[int] = mapped_column(Integer, default=1280, nullable=False)
    viewport_height: Mapped[int] = mapped_column(Integer, default=800, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    locale: Mapped[str] = mapped_column(String(32), default="en-US", nullable=False)
    timezone_id: Mapped[str] = mapped_column(String(64), default="America/New_York", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    tabs: Mapped[list["BrowserTabRecord"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class BrowserTabRecord(Base):
    __tablename__ = "browser_tabs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("browser_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    tab_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ready", nullable=False, index=True)  # active, navigating, ready, crashed, closed
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["BrowserSessionRecord"] = relationship(back_populates="tabs")


class BrowserTaskRecord(Base):
    __tablename__ = "browser_tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agent_id: Mapped[str] = mapped_column(String(64), default="browser_agent", nullable=False, index=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending, running, completed, failed, cancelled
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class BrowserActionRecord(Base):
    __tablename__ = "browser_actions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tab_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # navigate, click, fill, select, check, press_key, inspect_dom, download, screenshot
    target_locator: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending, executing, succeeded, failed, blocked
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String(256), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class BrowserProfileRecord(Base):
    __tablename__ = "browser_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    storage_path: Mapped[str] = mapped_column(String(256), nullable=False)
    is_authenticated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    domain_scopes_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class BrowserDownloadRecord(Base):
    __tablename__ = "browser_downloads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tab_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    suggested_filename: Mapped[str] = mapped_column(String(256), nullable=False)
    destination_path: Mapped[str] = mapped_column(String(256), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sha256_checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_url: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="in_progress", nullable=False, index=True)  # in_progress, completed, failed, cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


# ===========================================================================
# Stage 17: Windows Structural UI Automation Models
# ===========================================================================

class DesktopSessionRecord(Base):
    __tablename__ = "desktop_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    wts_session_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, index=True)  # active, locked, disconnected, unavailable
    desktop_name: Mapped[str] = mapped_column(String(128), default="Default", nullable=False)
    user_name: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    resolution: Mapped[str] = mapped_column(String(64), default="1920x1080", nullable=False)
    is_interactive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class DesktopApplicationRecord(Base):
    __tablename__ = "desktop_applications"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    executable_path: Mapped[str] = mapped_column(String(512), nullable=False)
    executable_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    publisher: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(32), default="LOW", nullable=False)
    integrity_level: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    last_detected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class DesktopWindowRecord(Base):
    __tablename__ = "desktop_windows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # window_ref: win_{hwnd}_{pid}
    hwnd: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    pid: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    window_class: Mapped[str] = mapped_column(String(256), default="", nullable=False)
    process_name: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_foreground: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_minimized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_maximized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bounds_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    last_inspected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DesktopTaskRecord(Base):
    __tablename__ = "desktop_tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agent_id: Mapped[str] = mapped_column(String(64), default="windows_computer_agent", nullable=False, index=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    target_app: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending, running, completed, failed, cancelled
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DesktopActionRecord(Base):
    __tablename__ = "desktop_actions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # invoke, set_value, select, toggle, expand, collapse, scroll, read_text, activate_window, close_window, press_key
    target_window_ref: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    target_element_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending, executing, succeeded, failed, blocked
    verification_status: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)  # verified, failed, unknown, skipped
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DesktopSnapshotRecord(Base):
    __tablename__ = "desktop_snapshots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    window_ref: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), default="", nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tree_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)


# =========================================================================
# Stage 18: Visual Computer Automation Records
# =========================================================================


class VisualCaptureSessionRecord(Base):
    __tablename__ = "visual_capture_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    target_type: Mapped[str] = mapped_column(String(32), default="display", nullable=False)
    target_hwnd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    display_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), default="mss", nullable=False)
    state: Mapped[str] = mapped_column(String(32), default="idle", nullable=False, index=True)
    frame_rate_limit: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    frames_captured: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class VisualFrameRecord(Base):
    __tablename__ = "visual_frames"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    frame_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    dpi_scale: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)


class VisualActionRecord(Base):
    __tablename__ = "visual_actions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    target_point_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_point_y: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_element: Mapped[str | None] = mapped_column(String(256), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="skipped", nullable=False)
    visual_difference: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)


class VisualTaskRecord(Base):
    __tablename__ = "visual_tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    steps_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


# =============================================================================
# Stage 19: Hybrid Computer Interaction & Multi-Method Automation Models
# =============================================================================

class HybridSessionRecord(Base):
    __tablename__ = "hybrid_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), default="Unified Session", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    browser_session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    desktop_window_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class HybridTaskRecord(Base):
    __tablename__ = "hybrid_tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    selected_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_surface: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fallback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RoutingDecisionRecord(Base):
    __tablename__ = "routing_decisions"

    decision_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    selected_method: Mapped[str] = mapped_column(String(32), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class MethodAttemptRecord(Base):
    __tablename__ = "method_attempts"

    attempt_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    method: Mapped[str] = mapped_column(String(32), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), default="not_verified", nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)







