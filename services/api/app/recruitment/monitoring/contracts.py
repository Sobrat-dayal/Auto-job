"""Domain contracts, Pydantic schemas, and enumerations for Stage 30 Recruitment Monitoring."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class WatchType(str, Enum):
    CAREER_STRATEGY = "career_strategy"
    SOURCE = "source"
    EMPLOYER = "employer"
    ROLE = "role"
    LOCATION = "location"
    SPECIFIC_JOB = "specific_job"
    SAVED_SEARCH = "saved_search"


class WatchStatus(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    REQUIRES_AUTHORIZATION = "requires_authorization"
    RATE_LIMITED = "rate_limited"
    FAILED = "failed"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class RunTriggerType(str, Enum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    RESUME_AFTER_RESTART = "resume_after_restart"
    SOURCE_CHANGE_EVENT = "source_change_event"
    CONFIG_CHANGED = "config_changed"
    RETRY = "retry"
    AUTHORIZED_AGENT = "authorized_agent"


class RunStatus(str, Enum):
    CREATED = "created"
    VALIDATING = "validating"
    QUEUED = "queued"
    WAITING_FOR_RESOURCES = "waiting_for_resources"
    WAITING_FOR_AUTHORIZATION = "waiting_for_authorization"
    RUNNING = "running"
    RATE_LIMITED = "rate_limited"
    PAUSED = "paused"
    PARTIALLY_COMPLETED = "partially_completed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class PipelinePhase(str, Enum):
    DISCOVERING = "discovering"
    AGGREGATING = "aggregating"
    ANALYZING = "analyzing"
    MATCHING = "matching"
    UPDATING_QUEUE = "updating_queue"
    EVALUATING_ALERTS = "evaluating_alerts"
    COMPLETED = "completed"


class JobChangeType(str, Enum):
    NEW_VACANCY = "new_vacancy"
    DESCRIPTION_UPDATED = "description_updated"
    SKILLS_CHANGED = "skills_changed"
    EXPERIENCE_CHANGED = "experience_changed"
    SALARY_CHANGED = "salary_changed"
    LOCATION_CHANGED = "location_changed"
    REMOTE_CONDITIONS_CHANGED = "remote_conditions_changed"
    DEADLINE_CHANGED = "deadline_changed"
    SPONSORSHIP_CHANGED = "sponsorship_changed"
    APPLICATION_URL_CHANGED = "application_url_changed"
    JOB_CLOSED = "job_closed"
    JOB_REOPENED = "job_reopened"


class OpportunityPriority(str, Enum):
    CRITICAL_REVIEW = "critical_review"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    DEFERRED = "deferred"
    EXCLUDED = "excluded"


class OpportunityQueueStatus(str, Enum):
    NEWLY_DISCOVERED = "newly_discovered"
    AWAITING_ANALYSIS = "awaiting_analysis"
    AWAITING_MATCH = "awaiting_match"
    RECOMMENDED = "recommended"
    HIGH_PRIORITY = "high_priority"
    NEEDS_REVIEW = "needs_review"
    READY_FOR_PREPARATION = "ready_for_preparation"
    DEFERRED = "deferred"
    SAVED = "saved"
    EXCLUDED = "excluded"
    CLOSED = "closed"
    OUTDATED = "outdated"
    ARCHIVED = "archived"
    PROCESSING_FAILED = "processing_failed"


class AlertTriggerType(str, Enum):
    NEW_JOB = "new_job"
    HIGH_PRIORITY_JOB = "high_priority_job"
    APPROACHING_DEADLINE = "approaching_deadline"
    MATERIAL_JOB_CHANGE = "material_job_change"
    JOB_CLOSED = "job_closed"
    JOB_REOPENED = "job_reopened"
    MATCH_CHANGED = "match_changed"
    REVIEW_REQUIRED = "review_required"
    SOURCE_FAILURE = "source_failure"
    PERMISSION_EXPIRED = "permission_expired"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class NotificationDeliveryStatus(str, Enum):
    PENDING = "pending"
    DEFERRED_BY_QUIET_HOURS = "deferred_by_quiet_hours"
    READY = "ready"
    DELIVERY_ATTEMPTED = "delivery_attempted"
    DELIVERED_WHERE_CONFIRMED = "delivered_where_confirmed"
    OUTCOME_UNKNOWN = "outcome_unknown"
    FAILED = "failed"
    DISMISSED = "dismissed"
    READ = "read"


class RecurrenceType(str, Enum):
    INTERVAL = "interval"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKDAYS = "weekdays"
    SELECTED_DAYS = "selected_days"
    WEEKLY = "weekly"
    CRON = "cron"


class MissedRunPolicy(str, Enum):
    SKIP = "skip"
    RUN_ONCE_AFTER_RESTART = "run_once_after_restart"
    RUN_LATEST_DUE = "run_latest_due"
    REQUIRE_REVIEW = "require_review"


class ComponentHealthStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    WAITING = "waiting"
    RATE_LIMITED = "rate_limited"
    PAUSED = "paused"
    NEEDS_AUTHORIZATION = "needs_authorization"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    DISABLED = "disabled"


# ---------------------------------------------------------------------------
# Schedule & Policy Schemas
# ---------------------------------------------------------------------------

class QuietHoursConfig(BaseModel):
    enabled: bool = True
    start_time: str = Field(default="22:00", description="HH:MM in local timezone")
    end_time: str = Field(default="08:00", description="HH:MM in local timezone")
    mute_notifications: bool = True
    pause_source_monitoring: bool = False
    pause_heavy_inference: bool = True


class ScheduleConfig(BaseModel):
    recurrence_type: RecurrenceType = RecurrenceType.INTERVAL
    interval_minutes: int = Field(default=60, ge=5, le=10080, description="Minimum 5 minutes")
    cron_expression: Optional[str] = None
    days_of_week: list[int] = Field(default_factory=list, description="0=Monday, 6=Sunday")
    time_of_day: Optional[str] = Field(default="09:00", description="HH:MM for daily/weekly schedules")
    timezone: str = Field(default="UTC", description="IANA timezone name")
    quiet_hours: QuietHoursConfig = Field(default_factory=QuietHoursConfig)
    missed_run_policy: MissedRunPolicy = MissedRunPolicy.RUN_LATEST_DUE
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=300, ge=30)


class SchedulePreviewOccurrence(BaseModel):
    occurrence_index: int
    scheduled_time: datetime
    is_quiet_hours: bool
    action: str  # "execute", "defer_notifications", "skip"


class SchedulePreviewResponse(BaseModel):
    watch_name: str
    timezone: str
    recurrence_summary: str
    next_occurrences: list[SchedulePreviewOccurrence]
    estimated_request_budget_per_run: int
    quiet_hours_active_in_preview: bool
    requires_authorization: bool


# ---------------------------------------------------------------------------
# Profile & Watch Models
# ---------------------------------------------------------------------------

class MonitoringProfileCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    career_strategy_id: Optional[str] = None
    source_scope: list[str] = Field(default_factory=list)
    role_scope: list[str] = Field(default_factory=list)
    location_scope: list[str] = Field(default_factory=list)
    alert_preferences: dict[str, Any] = Field(default_factory=dict)
    resource_limits: dict[str, Any] = Field(default_factory=dict)
    review_rules: dict[str, Any] = Field(default_factory=dict)
    retention_days: int = Field(default=90, ge=7, le=365)


class MonitoringProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    career_strategy_id: Optional[str] = None
    enabled: Optional[bool] = None
    source_scope: Optional[list[str]] = None
    role_scope: Optional[list[str]] = None
    location_scope: Optional[list[str]] = None
    alert_preferences: Optional[dict[str, Any]] = None
    resource_limits: Optional[dict[str, Any]] = None
    review_rules: Optional[dict[str, Any]] = None
    retention_days: Optional[int] = None


class MonitoringProfileData(BaseModel):
    id: str
    owner_id: str
    career_strategy_id: Optional[str] = None
    career_strategy_version: Optional[int] = None
    name: str
    enabled: bool
    source_scope: list[str]
    role_scope: list[str]
    location_scope: list[str]
    alert_preferences: dict[str, Any]
    resource_limits: dict[str, Any]
    review_rules: dict[str, Any]
    retention_days: int
    version: int
    active_watches_count: int = 0
    created_at: datetime
    updated_at: datetime


class JobWatchCreateRequest(BaseModel):
    profile_id: str
    name: str = Field(..., min_length=2, max_length=128)
    watch_type: WatchType = WatchType.CAREER_STRATEGY
    career_strategy_id: Optional[str] = None
    approved_sources: list[str] = Field(default_factory=list)
    employer_ids: list[str] = Field(default_factory=list)
    role_filters: dict[str, Any] = Field(default_factory=dict)
    location_filters: dict[str, Any] = Field(default_factory=dict)
    schedule_config: ScheduleConfig = Field(default_factory=ScheduleConfig)
    alert_rules: dict[str, Any] = Field(default_factory=dict)


class JobWatchUpdateRequest(BaseModel):
    name: Optional[str] = None
    approved_sources: Optional[list[str]] = None
    employer_ids: Optional[list[str]] = None
    role_filters: Optional[dict[str, Any]] = None
    location_filters: Optional[dict[str, Any]] = None
    schedule_config: Optional[ScheduleConfig] = None
    alert_rules: Optional[dict[str, Any]] = None
    status: Optional[WatchStatus] = None


class JobWatchData(BaseModel):
    id: str
    owner_id: str
    profile_id: str
    name: str
    watch_type: WatchType
    career_strategy_id: Optional[str] = None
    approved_sources: list[str]
    employer_ids: list[str]
    role_filters: dict[str, Any]
    location_filters: dict[str, Any]
    schedule_config: ScheduleConfig
    alert_rules: dict[str, Any]
    status: WatchStatus
    error_state: Optional[str] = None
    last_run_at: Optional[datetime] = None
    next_due_run_at: Optional[datetime] = None
    consecutive_failures: int = 0
    version: int = 1
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Monitoring Run Models
# ---------------------------------------------------------------------------

class MonitoringRunData(BaseModel):
    id: str
    watch_id: str
    watch_version: int
    trigger_type: RunTriggerType
    scheduled_at: Optional[datetime] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    sources_checked_list: list[str] = Field(default_factory=list)
    current_phase: PipelinePhase
    status: RunStatus
    progress_pct: float
    sources_checked: int = 0
    new_observations_count: int = 0
    updated_observations_count: int = 0
    canonical_jobs_created: int = 0
    canonical_jobs_updated: int = 0
    intelligence_analyses_triggered: int = 0
    matches_recalculated: int = 0
    queue_entries_created: int = 0
    alerts_generated: int = 0
    error_message: Optional[str] = None
    output_references: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Change Events
# ---------------------------------------------------------------------------

class JobChangeEventData(BaseModel):
    id: str
    canonical_job_id: str
    source_id: Optional[str] = None
    run_id: Optional[str] = None
    change_type: JobChangeType
    is_material: bool
    field_name: str
    previous_value: Any = None
    current_value: Any = None
    detected_at: datetime


# ---------------------------------------------------------------------------
# Opportunity Queue & Future Stage 31 Handoff
# ---------------------------------------------------------------------------

class OpportunityPreparationCandidate(BaseModel):
    """Stage 31 Integration Contract: Hand-off candidate for application preparation."""
    canonical_job_id: str
    canonical_job_version: str
    job_title: str
    company_name: str
    application_url: str
    applicant_profile_id: str
    applicant_profile_version: str
    job_intelligence_version: str
    match_evaluation_id: str
    relevance_score: float
    eligibility_outcome: str
    career_strategy_id: Optional[str] = None
    policy_version: int = 1
    priority: OpportunityPriority
    current_job_status: str
    deadline: Optional[datetime] = None
    missing_information: list[str] = Field(default_factory=list)
    required_reviews: list[dict[str, Any]] = Field(default_factory=list)
    ready_for_preparation: bool = True
    generated_at: datetime


class OpportunityQueueEntryData(BaseModel):
    id: str
    canonical_job_id: str
    job_title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    salary_range: Optional[str] = None
    application_url: str
    applicant_profile_id: str
    career_strategy_id: Optional[str] = None
    match_evaluation_id: Optional[str] = None
    priority: OpportunityPriority
    queue_status: OpportunityQueueStatus
    eligibility_state: str
    policy_state: str
    review_requirements: list[dict[str, Any]] = Field(default_factory=list)
    job_availability: str
    deadline: Optional[datetime] = None
    relevance_score: Optional[float] = None
    user_action: Optional[str] = None
    user_action_at: Optional[datetime] = None
    ready_for_preparation: bool = False
    stage31_candidate: Optional[OpportunityPreparationCandidate] = None
    version: int = 1
    created_at: datetime
    updated_at: datetime


class OpportunityQueueUpdateRequest(BaseModel):
    priority: Optional[OpportunityPriority] = None
    queue_status: Optional[OpportunityQueueStatus] = None
    user_action: Optional[str] = None  # save, prioritize, deprioritize, defer, exclude, archive


# ---------------------------------------------------------------------------
# Alerts & Notifications
# ---------------------------------------------------------------------------

class AlertRuleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    profile_id: Optional[str] = None
    watch_id: Optional[str] = None
    trigger_type: AlertTriggerType
    conditions: dict[str, Any] = Field(default_factory=dict)
    delivery_channels: list[str] = Field(default_factory=lambda: ["in_app", "windows_desktop"])
    quiet_hours_enabled: bool = True
    cooldown_minutes: int = Field(default=60, ge=0)


class AlertRuleUpdateRequest(BaseModel):
    name: Optional[str] = None
    trigger_type: Optional[AlertTriggerType] = None
    conditions: Optional[dict[str, Any]] = None
    delivery_channels: Optional[list[str]] = None
    quiet_hours_enabled: Optional[bool] = None
    cooldown_minutes: Optional[int] = None
    enabled: Optional[bool] = None


class AlertRuleData(BaseModel):
    id: str
    owner_id: str
    name: str
    profile_id: Optional[str] = None
    watch_id: Optional[str] = None
    trigger_type: AlertTriggerType
    conditions: dict[str, Any]
    delivery_channels: list[str]
    quiet_hours_enabled: bool
    cooldown_minutes: int
    enabled: bool
    version: int
    created_at: datetime
    updated_at: datetime


class AlertEventData(BaseModel):
    id: str
    owner_id: str
    rule_id: Optional[str] = None
    queue_entry_id: Optional[str] = None
    canonical_job_id: Optional[str] = None
    run_id: Optional[str] = None
    title: str
    message: str
    alert_type: AlertTriggerType
    severity: AlertSeverity
    is_read: bool
    is_dismissed: bool
    acknowledged_at: Optional[datetime] = None
    deep_link: Optional[str] = None
    created_at: datetime


class NotificationOutboxData(BaseModel):
    id: str
    alert_event_id: str
    delivery_channel: str
    title: str
    body: str
    status: NotificationDeliveryStatus
    attempts: int
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    deferred_until: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Settings, Health, Metrics & Diagnostics
# ---------------------------------------------------------------------------

class MonitoringSettingsData(BaseModel):
    owner_id: str
    background_monitoring_enabled: bool = True
    start_at_windows_signin: bool = False
    minimize_to_tray: bool = True
    default_interval_minutes: int = 60
    global_concurrency_limit: int = 3
    daily_request_budget: int = 500
    pause_on_battery: bool = False
    quiet_hours_enabled: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"
    notification_privacy_mode: bool = True
    retention_days: int = 90
    updated_at: datetime


class MonitoringSettingsUpdateRequest(BaseModel):
    background_monitoring_enabled: Optional[bool] = None
    start_at_windows_signin: Optional[bool] = None
    minimize_to_tray: Optional[bool] = None
    default_interval_minutes: Optional[int] = None
    global_concurrency_limit: Optional[int] = None
    daily_request_budget: Optional[int] = None
    pause_on_battery: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    notification_privacy_mode: Optional[bool] = None
    retention_days: Optional[int] = None


class MonitoringOverviewKPIs(BaseModel):
    monitoring_enabled: bool
    active_watches_count: int
    next_scheduled_run_at: Optional[datetime] = None
    last_successful_run_at: Optional[datetime] = None
    currently_running_runs_count: int = 0
    total_opportunities_count: int = 0
    high_priority_count: int = 0
    review_required_count: int = 0
    ready_for_preparation_count: int = 0
    unread_alerts_count: int = 0
    source_failures_count: int = 0


class MonitoringMetricsData(BaseModel):
    total_runs_executed: int = 0
    successful_runs_count: int = 0
    failed_runs_count: int = 0
    total_requests_attempted: int = 0
    total_requests_successful: int = 0
    rate_limited_responses_count: int = 0
    new_source_observations_count: int = 0
    new_canonical_jobs_count: int = 0
    changed_canonical_jobs_count: int = 0
    intelligence_analyses_count: int = 0
    matches_recalculated_count: int = 0
    queue_entries_created_count: int = 0
    alerts_generated_count: int = 0
    notifications_delivered_count: int = 0
    average_run_latency_seconds: float = 0.0


class ComponentHealthData(BaseModel):
    component: str
    status: ComponentHealthStatus
    heartbeat_at: datetime
    details: dict[str, Any] = Field(default_factory=dict)


class DiagnosticsReport(BaseModel):
    system_time_utc: datetime
    timezone_configured: str
    is_quiet_hours_now: bool
    database_status: str
    emergency_stop_active: bool
    automation_paused: bool
    active_worker_leases: int
    pending_outbox_notifications: int
    components_health: list[ComponentHealthData]
    active_cooldowns: list[dict[str, Any]]
