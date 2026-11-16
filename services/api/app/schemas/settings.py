"""Pydantic schemas for the centralized AUTONOM settings system."""

from typing import Any, Literal

from pydantic import BaseModel, Field


# ==============================================================================
# 1. GENERAL SETTINGS
# ==============================================================================
class GeneralSettings(BaseModel):
    app_language: str = Field(default="en-US", description="Application display language locale")
    date_format: Literal["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"] = Field(
        default="YYYY-MM-DD", description="Preferred date presentation format"
    )
    time_format: Literal["24h", "12h"] = Field(default="24h", description="Preferred clock presentation format")
    timezone_display: Literal["UTC", "Local"] = Field(
        default="Local", description="Timezone representation for displayed timestamps"
    )
    default_landing_page: str = Field(default="/dashboard", description="Default route when opening the application")
    confirm_destructive_actions: bool = Field(
        default=True, description="Prompt confirmation modal before destructive actions"
    )
    confirm_backup_restore: bool = Field(
        default=True, description="Require two-step confirmation before restoring database snapshots"
    )
    confirm_task_cancellation: bool = Field(
        default=True, description="Prompt confirmation before terminating executing tasks"
    )
    show_technical_metrics: bool = Field(
        default=True, description="Display hardware memory and latency metrics in the UI"
    )
    high_contrast_borders: bool = Field(default=False, description="Enable accessibility high-contrast surface borders")


# ==============================================================================
# 2. APPEARANCE SETTINGS
# ==============================================================================
class AppearanceSettings(BaseModel):
    theme: Literal["dark", "navy-dark"] = Field(default="navy-dark", description="Visual color theme")
    density: Literal["comfortable", "compact"] = Field(
        default="comfortable", description="UI element spacing and padding mode"
    )
    font_scale: Literal["90%", "100%", "110%"] = Field(default="100%", description="Global UI font size multiplier")
    sidebar_default_expanded: bool = Field(default=True, description="Expand the sidebar by default on launch")
    reduced_motion: bool = Field(default=False, description="Disable transition animations and visual effects")
    chart_animations: bool = Field(default=True, description="Enable animated transitions in analytics charts")
    table_density: Literal["compact", "normal"] = Field(
        default="normal", description="Padding density inside data tables"
    )


# ==============================================================================
# 3. AI PROVIDERS & MODELS SETTINGS
# ==============================================================================
class AIProviderItem(BaseModel):
    id: str = Field(description="Unique provider identifier, e.g. 'ollama', 'openai', 'anthropic'")
    name: str = Field(description="Display name of the provider")
    provider_type: Literal["local", "cloud", "custom"] = Field(
        default="local", description="Deployment modality of the provider"
    )
    endpoint: str = Field(default="http://localhost:11434", description="Base HTTP/REST or socket URL")
    auth_method: Literal["none", "bearer_token", "api_key"] = Field(
        default="none", description="Authentication protocol"
    )
    credential_ref: str | None = Field(
        default=None, description="Reference ID in secure Windows DPAPI credential store"
    )
    enabled: bool = Field(default=True, description="Whether this provider is active for selection")
    connection_status: Literal["unconfigured", "configured", "offline", "verified"] = Field(
        default="unconfigured", description="Last known health status of the provider endpoint"
    )
    last_verified_at: str | None = Field(
        default=None, description="ISO-8601 timestamp of last successful connectivity verification"
    )
    supported_modalities: list[str] = Field(
        default_factory=lambda: ["text", "code"], description="Supported model modalities"
    )


class AIModelItem(BaseModel):
    id: str = Field(description="Model identifier, e.g. 'llama3.2:3b', 'qwen2.5-coder:7b'")
    name: str = Field(description="User-friendly name of the model")
    provider_id: str = Field(description="Target provider ID")
    task_category: Literal["scouting", "synthesis", "coding", "analysis", "general"] = Field(
        default="general", description="Primary agent task assignment"
    )
    context_window: int = Field(default=8192, description="Maximum context window tokens")
    max_output_tokens: int = Field(default=2048, description="Maximum completion tokens")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="Sampling temperature")
    timeout_seconds: int = Field(default=60, ge=5, le=600, description="Inference timeout")
    fallback_model_id: str | None = Field(default=None, description="Fallback model ID if primary inference fails")


class AISettings(BaseModel):
    providers: list[AIProviderItem] = Field(
        default_factory=lambda: [
            AIProviderItem(
                id="ollama",
                name="Ollama Local Engine",
                provider_type="local",
                endpoint="http://localhost:11434",
                auth_method="none",
                enabled=True,
                connection_status="unconfigured",
                supported_modalities=["text", "code"],
            ),
            AIProviderItem(
                id="openai",
                name="OpenAI API",
                provider_type="cloud",
                endpoint="https://api.openai.com/v1",
                auth_method="api_key",
                enabled=False,
                connection_status="unconfigured",
                supported_modalities=["text", "code", "vision"],
            ),
            AIProviderItem(
                id="anthropic",
                name="Anthropic Claude API",
                provider_type="cloud",
                endpoint="https://api.anthropic.com/v1",
                auth_method="api_key",
                enabled=False,
                connection_status="unconfigured",
                supported_modalities=["text", "code", "vision"],
            ),
        ],
        description="Configured AI model providers",
    )
    models: list[AIModelItem] = Field(
        default_factory=lambda: [
            AIModelItem(
                id="llama3.2:3b",
                name="Llama 3.2 3B (Fast Reasoning)",
                provider_id="ollama",
                task_category="scouting",
                context_window=8192,
                max_output_tokens=2048,
                temperature=0.2,
            ),
            AIModelItem(
                id="qwen2.5-coder:7b",
                name="Qwen 2.5 Coder 7B (Code & Scripting)",
                provider_id="ollama",
                task_category="coding",
                context_window=16384,
                max_output_tokens=4096,
                temperature=0.1,
            ),
        ],
        description="Configured model specifications",
    )
    single_active_model_enforced: bool = Field(
        default=True,
        description="Enforce single loaded model in VRAM for RTX 4050 (6GB) compliance",
    )
    max_vram_allocation_mb: int = Field(
        default=5120,
        ge=1024,
        le=6144,
        description="Maximum VRAM allocation budget in megabytes (Target: 6GB GPU)",
    )
    idle_model_unload_seconds: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Unload idle model from VRAM after inactivity seconds",
    )
    cloud_fallback_enabled: bool = Field(
        default=False,
        description="Allow cloud API fallback when local GPU VRAM is constrained",
    )


# ==============================================================================
# 4. AGENT PREFERENCES
# ==============================================================================
class AgentConfigItem(BaseModel):
    agent_id: str = Field(description="Unique identifier for the agent")
    role: str = Field(description="Agent functional role")
    enabled: bool = Field(default=True, description="Whether this agent can be dispatched")
    preferred_model_id: str = Field(default="llama3.2:3b", description="Preferred model")
    execution_priority: Literal["low", "normal", "high"] = Field(
        default="normal", description="Worker task queue priority"
    )
    max_concurrent_tasks: int = Field(default=1, ge=1, le=4, description="Maximum concurrent tasks for this agent")
    max_execution_duration_seconds: int = Field(default=120, ge=10, le=1800, description="Maximum execution timeout")
    human_approval_requirement: Literal["always", "sensitive_only", "never"] = Field(
        default="sensitive_only", description="Level of human-in-the-loop oversight"
    )
    memory_access_policy: Literal["read_only", "workspace_only", "full"] = Field(
        default="workspace_only", description="Memory and file access boundary"
    )


class AgentSettings(BaseModel):
    agents: list[AgentConfigItem] = Field(
        default_factory=lambda: [
            AgentConfigItem(
                agent_id="scout-primary",
                role="Job Discovery Scout",
                enabled=True,
                preferred_model_id="llama3.2:3b",
                execution_priority="normal",
                max_concurrent_tasks=1,
                max_execution_duration_seconds=120,
                human_approval_requirement="never",
            ),
            AgentConfigItem(
                agent_id="scribe-tailor",
                role="Resume & Dossier Tailor",
                enabled=True,
                preferred_model_id="qwen2.5-coder:7b",
                execution_priority="high",
                max_concurrent_tasks=1,
                max_execution_duration_seconds=180,
                human_approval_requirement="sensitive_only",
            ),
            AgentConfigItem(
                agent_id="executor-submitter",
                role="Application Submitter",
                enabled=True,
                preferred_model_id="llama3.2:3b",
                execution_priority="high",
                max_concurrent_tasks=1,
                max_execution_duration_seconds=300,
                human_approval_requirement="always",
            ),
        ],
        description="Agent behavioral configurations",
    )
    default_autonomy_level: Literal["tier1_full", "tier2_supervised", "tier3_manual"] = Field(
        default="tier2_supervised", description="Default system autonomy tier"
    )
    auto_retry_failed_tasks: bool = Field(default=True, description="Automatically retry idempotent task failures")
    max_agent_retries: int = Field(default=2, ge=0, le=5, description="Maximum retry count")


# ==============================================================================
# 5. AUTOMATION & TASK EXECUTION
# ==============================================================================
class AutomationSettings(BaseModel):
    max_concurrent_workers: int = Field(
        default=4, ge=1, le=8, description="Maximum asynchronous worker threads/coroutines"
    )
    max_queued_tasks: int = Field(default=50, ge=10, le=200, description="Maximum bounded task queue depth")
    task_default_timeout_seconds: float = Field(
        default=60.0, ge=5.0, le=600.0, description="Default execution timeout for tasks"
    )
    retry_limit: int = Field(default=3, ge=0, le=10, description="Maximum automatic retries for transient errors")
    background_dispatch_enabled: bool = Field(default=True, description="Enable automated background task dispatching")
    task_history_retention_days: int = Field(
        default=30, ge=1, le=365, description="Days to retain completed task logs in SQLite"
    )
    notify_on_task_failure: bool = Field(default=True, description="Dispatch toast notifications when tasks fail")
    pause_dispatch_on_error_spike: bool = Field(
        default=True, description="Pause task queue if failure rate exceeds 50%"
    )


# ==============================================================================
# 6. AUTHORIZATION & PERMISSIONS
# ==============================================================================
class PermissionCategoryRule(BaseModel):
    category_id: str = Field(description="Permission category identifier")
    name: str = Field(description="Human readable permission category name")
    allowed: bool = Field(default=True, description="Whether this category of action is enabled")
    requires_approval: bool = Field(default=False, description="Require human approval before execution")
    description: str = Field(description="Description of what this permission grants")


class PermissionSettings(BaseModel):
    permissions: list[PermissionCategoryRule] = Field(
        default_factory=lambda: [
            PermissionCategoryRule(
                category_id="read_data",
                name="Read Data",
                allowed=True,
                requires_approval=False,
                description="Read local workspace files, job listings, and stored profiles",
            ),
            PermissionCategoryRule(
                category_id="write_data",
                name="Write Data",
                allowed=True,
                requires_approval=False,
                description="Write task logs, cache records, and temporary analytical data",
            ),
            PermissionCategoryRule(
                category_id="create_files",
                name="Create Files",
                allowed=True,
                requires_approval=False,
                description="Generate tailored resumes, cover letters, and research briefs",
            ),
            PermissionCategoryRule(
                category_id="modify_files",
                name="Modify Files",
                allowed=True,
                requires_approval=True,
                description="Modify existing files in local workspace projects",
            ),
            PermissionCategoryRule(
                category_id="delete_files",
                name="Delete Files",
                allowed=False,
                requires_approval=True,
                description="Delete artifacts or workspace documents",
            ),
            PermissionCategoryRule(
                category_id="browse_websites",
                name="Browse Websites",
                allowed=True,
                requires_approval=False,
                description="Scout career boards and employer portals via Playwright",
            ),
            PermissionCategoryRule(
                category_id="control_applications",
                name="Control Applications",
                allowed=False,
                requires_approval=True,
                description="Interact with desktop applications via Windows UI Automation",
            ),
            PermissionCategoryRule(
                category_id="execute_code",
                name="Execute Code",
                allowed=False,
                requires_approval=True,
                description="Execute local terminal scripts, compilers, or test runners",
            ),
            PermissionCategoryRule(
                category_id="send_communications",
                name="Send Communications",
                allowed=False,
                requires_approval=True,
                description="Send emails, LinkedIn messages, or recruiter replies",
            ),
            PermissionCategoryRule(
                category_id="submit_applications",
                name="Submit Applications",
                allowed=False,
                requires_approval=True,
                description="Submit completed job applications to employer ATS portals",
            ),
            PermissionCategoryRule(
                category_id="access_credentials",
                name="Access Credentials",
                allowed=True,
                requires_approval=True,
                description="Retrieve credentials from Windows DPAPI secure vault",
            ),
            PermissionCategoryRule(
                category_id="manage_integrations",
                name="Manage Integrations",
                allowed=True,
                requires_approval=True,
                description="Configure external APIs, MCP servers, and cloud providers",
            ),
            PermissionCategoryRule(
                category_id="destructive_actions",
                name="Destructive Actions",
                allowed=False,
                requires_approval=True,
                description="Database restoration, complete data wipe, or credential revocation",
            ),
            PermissionCategoryRule(
                category_id="modify_security_settings",
                name="Modify Security Settings",
                allowed=True,
                requires_approval=True,
                description="Modify autonomy tiers, permission gates, or killswitch keys",
            ),
        ],
        description="Comprehensive permission policy rules",
    )
    emergency_killswitch_hotkey: str = Field(
        default="Pause", description="Hardware interrupt hotkey to pause all automation"
    )
    preauthorize_discovery: bool = Field(default=True, description="Preauthorize read-only job discovery and scouting")
    preauthorize_dossier_prep: bool = Field(
        default=True, description="Preauthorize drafting of tailored resumes and cover letters"
    )


# ==============================================================================
# 7. COMPUTER CONTROL SETTINGS
# ==============================================================================
class ComputerControlSettings(BaseModel):
    preferred_interaction_mode: Literal["structural_first", "visual_first", "structural_only"] = Field(
        default="structural_first",
        description="Prefer Windows UIA/DOM, falling back to visual coordinates",
    )
    visual_fallback_enabled: bool = Field(
        default=True, description="Allow vision-model coordinate grounding when UIA is unsupported"
    )
    idle_capture_interval_seconds: float = Field(
        default=5.0, ge=1.0, le=60.0, description="Screenshot capture interval when idle"
    )
    active_capture_interval_seconds: float = Field(
        default=1.0, ge=0.5, le=10.0, description="Screenshot capture interval during active tasks"
    )
    burst_capture_interval_seconds: float = Field(
        default=0.2, ge=0.1, le=2.0, description="High-frequency burst interval during actions"
    )
    screenshot_retention_hours: int = Field(
        default=24, ge=1, le=168, description="Hours to retain debug screenshots on local disk"
    )
    sensitive_region_redaction: bool = Field(
        default=True,
        description="Automatically mask password inputs, bank fields, and credential forms",
    )
    allowed_applications: list[str] = Field(
        default_factory=lambda: ["chrome.exe", "msedge.exe", "code.exe", "notepad.exe"],
        description="Process names permitted for automated interaction",
    )
    blocked_applications: list[str] = Field(
        default_factory=lambda: [
            "regedit.exe",
            "cmd.exe",
            "powershell.exe",
            "taskmgr.exe",
            "keepass.exe",
            "1password.exe",
        ],
        description="Process names strictly blocked from autonomous interaction",
    )
    mouse_keyboard_control_enabled: bool = Field(
        default=False,
        description="Allow autonomous mouse clicking and keyboard typing (Stage 17-18)",
    )
    session_timeout_minutes: int = Field(
        default=30, ge=5, le=240, description="Maximum computer control session duration"
    )


# ==============================================================================
# 8. CONNECTED SERVICES & MCP SETTINGS
# ==============================================================================
class MCPServerConfigItem(BaseModel):
    server_id: str = Field(description="Unique identifier for the MCP server")
    name: str = Field(description="Display name")
    transport: Literal["stdio", "sse"] = Field(default="stdio", description="Communication protocol transport")
    command_or_url: str = Field(description="Executable path, command string, or SSE endpoint")
    enabled: bool = Field(default=False, description="Whether this MCP server is enabled")
    trusted: bool = Field(default=False, description="User trust authorization for tool invocation")
    allowed_tools: list[str] = Field(default_factory=list, description="Explicit list of permitted tool names")


class IntegrationSettings(BaseModel):
    mcp_servers: list[MCPServerConfigItem] = Field(
        default_factory=lambda: [
            MCPServerConfigItem(
                server_id="filesystem",
                name="Local Filesystem MCP",
                transport="stdio",
                command_or_url="npx -y @modelcontextprotocol/server-filesystem",
                enabled=False,
                trusted=False,
                allowed_tools=["read_file", "list_directory"],
            ),
            MCPServerConfigItem(
                server_id="github",
                name="GitHub Integration MCP",
                transport="stdio",
                command_or_url="npx -y @modelcontextprotocol/server-github",
                enabled=False,
                trusted=False,
                allowed_tools=["search_repositories", "get_file_contents"],
            ),
        ],
        description="Configured Model Context Protocol servers",
    )
    email_integration_enabled: bool = Field(default=False, description="Enable recruitment email monitoring (Stage 36)")
    telegram_integration_enabled: bool = Field(
        default=False, description="Enable Telegram notifications and alerts (Stage 36)"
    )
    whatsapp_integration_enabled: bool = Field(
        default=False, description="Enable WhatsApp recruiter communications (Stage 36)"
    )
    job_board_scouting_enabled: bool = Field(default=True, description="Enable automated job board indexing")


# ==============================================================================
# 9. RECRUITMENT PREFERENCES
# ==============================================================================
class RecruitmentSettings(BaseModel):
    desired_job_titles: list[str] = Field(
        default_factory=lambda: [
            "Software Engineer",
            "Full Stack Developer",
            "Python Backend Engineer",
            "AI Engineer",
        ],
        description="Target job titles to scout and match",
    )
    related_job_titles: list[str] = Field(
        default_factory=lambda: [
            "Systems Software Engineer",
            "Platform Engineer",
            "React Developer",
        ],
        description="Secondary acceptable job titles",
    )
    role_levels: list[Literal["internship", "entry", "mid", "senior", "lead"]] = Field(
        default_factory=lambda: ["entry", "mid"], description="Target seniority levels"
    )
    preferred_locations: list[str] = Field(
        default_factory=lambda: ["Remote", "Bengaluru", "San Francisco", "London"],
        description="Preferred geographic locations",
    )
    work_style: list[Literal["remote", "hybrid", "onsite"]] = Field(
        default_factory=lambda: ["remote", "hybrid"], description="Acceptable work arrangements"
    )
    relocation_willing: bool = Field(default=False, description="Willingness to relocate")
    minimum_base_salary: int = Field(
        default=0, ge=0, description="Minimum acceptable annual compensation (0 for unconstrained)"
    )
    salary_currency: str = Field(default="USD", description="Currency for compensation figures")
    excluded_companies: list[str] = Field(
        default_factory=list, description="Company names to strictly exclude from applications"
    )
    excluded_sources: list[str] = Field(default_factory=list, description="Job boards or platforms to skip")
    max_daily_applications: int = Field(
        default=5, ge=1, le=25, description="Maximum automated job applications per 24-hour cycle"
    )
    application_window_start: str = Field(
        default="09:00", description="Earliest time of day for autonomous submissions (HH:MM)"
    )
    application_window_end: str = Field(
        default="18:00", description="Latest time of day for autonomous submissions (HH:MM)"
    )
    prevent_duplicate_applications: bool = Field(
        default=True, description="Prevent applying to the same company/role within 90 days"
    )
    minimum_match_threshold: int = Field(
        default=75, ge=50, le=100, description="Minimum ATS match percentage required to apply"
    )
    resume_tailoring_mode: Literal["subtle", "focused", "comprehensive"] = Field(
        default="focused", description="Depth of resume tailoring per job description"
    )
    require_human_approval_for_submission: bool = Field(
        default=True,
        description="Require explicit user sign-off before submitting any job application (Tier 2)",
    )
    auto_submission_authorized: bool = Field(
        default=False,
        description="Authorize fully autonomous application submission (Stage 31)",
    )


# ==============================================================================
# 10. STORAGE & DATA SETTINGS
# ==============================================================================
class StorageSettings(BaseModel):
    backup_retention_count: int = Field(
        default=10, ge=3, le=50, description="Number of database backup snapshots to retain"
    )
    data_retention_days: int = Field(
        default=90, ge=7, le=365, description="Retention window for diagnostic and task history"
    )
    auto_backup_on_startup: bool = Field(default=True, description="Create an online SQLite snapshot on desktop launch")
    auto_vacuum_enabled: bool = Field(
        default=True, description="Run incremental PRAGMA incremental_vacuum periodically"
    )
    artifact_storage_limit_mb: int = Field(
        default=2048, ge=512, le=20480, description="Disk quota in megabytes for generated artifacts"
    )


# ==============================================================================
# 11. NOTIFICATIONS SETTINGS
# ==============================================================================
class NotificationSettings(BaseModel):
    notifications_enabled: bool = Field(
        default=True, description="Master toggle for all desktop and in-app notifications"
    )
    notify_on_task_completion: bool = Field(
        default=True, description="Notify when a background task completes successfully"
    )
    notify_on_task_failure: bool = Field(default=True, description="Notify when a background task fails")
    notify_on_backend_events: bool = Field(
        default=True, description="Notify on backend process restart, supervisor warning, or error"
    )
    notify_on_pending_approval: bool = Field(
        default=True, description="Notify when an autonomous action requires human sign-off"
    )
    quiet_hours_enabled: bool = Field(default=False, description="Suppress sound and desktop popups during quiet hours")
    quiet_hours_start: str = Field(default="22:00", description="Quiet hours start (HH:MM)")
    quiet_hours_end: str = Field(default="08:00", description="Quiet hours end (HH:MM)")
    sound_enabled: bool = Field(default=True, description="Play audio chime with notifications")
    mask_sensitive_previews: bool = Field(
        default=True,
        description="Hide applicant names and salary details in Windows Action Center toasts",
    )


# ==============================================================================
# 12. DESKTOP & STARTUP SETTINGS
# ==============================================================================
class DesktopSettings(BaseModel):
    start_at_login: bool = Field(default=False, description="Launch AUTONOM desktop automatically on Windows login")
    close_to_tray: bool = Field(
        default=True,
        description="Minimizing or closing the window leaves AUTONOM running in the Windows system tray",
    )
    minimize_to_tray: bool = Field(default=True, description="Minimize window to system notification area")
    restore_window_position: bool = Field(
        default=True, description="Restore previous multi-monitor window coordinates on startup"
    )
    auto_start_backend_sidecar: bool = Field(
        default=True, description="Automatically start and supervise Python FastAPI backend process"
    )
    max_backend_restarts: int = Field(
        default=5, ge=1, le=20, description="Maximum automatic restarts if backend crashes"
    )


# ==============================================================================
# 13. SECURITY & PRIVACY SETTINGS
# ==============================================================================
class SecurityPrivacySettings(BaseModel):
    dpapi_vault_enabled: bool = Field(default=True, description="Use Windows DPAPI user-scope key wrapping for secrets")
    redact_secrets_in_logs: bool = Field(
        default=True, description="Strictly redact API keys, bearer tokens, and credentials in logs"
    )
    audit_logging_level: Literal["all_actions", "sensitive_only", "security_only"] = Field(
        default="all_actions", description="Granularity of immutable security audit logs"
    )
    local_first_strict_mode: bool = Field(
        default=True,
        description="Ensure zero external network traffic unless explicit cloud provider is configured",
    )
    telemetry_enabled: bool = Field(
        default=False,
        description="Local diagnostic telemetry only (never uploaded to remote servers)",
    )


# ==============================================================================
# AGGREGATED SETTINGS CONTAINER & REGISTRY METADATA
# ==============================================================================
class AllSettingsResponse(BaseModel):
    general: GeneralSettings
    appearance: AppearanceSettings
    ai: AISettings
    agents: AgentSettings
    automation: AutomationSettings
    permissions: PermissionSettings
    computer: ComputerControlSettings
    integrations: IntegrationSettings
    recruitment: RecruitmentSettings
    storage: StorageSettings
    notifications: NotificationSettings
    desktop: DesktopSettings
    security: SecurityPrivacySettings
    version: int = Field(default=1, description="Settings schema revision")
    last_updated_at: str | None = Field(default=None, description="ISO timestamp of last settings change")


class SettingCategoryUpdate(BaseModel):
    value: dict[str, Any] = Field(description="JSON dictionary for category settings payload")


class SettingItemMetadata(BaseModel):
    key: str
    category: str
    setting_type: str
    default_value: Any
    description: str
    requires_restart: bool = False
    is_sensitive: bool = False
    availability: Literal["available", "planned"] = "available"
    roadmap_stage: str | None = None


class SettingsSchemaMetadataResponse(BaseModel):
    schema_version: int = 1
    categories: list[str]
    items: list[SettingItemMetadata]


class SettingsExportPayload(BaseModel):
    app_version: str
    exported_at: str
    schema_version: int = 1
    settings: dict[str, Any]


class SettingsImportPayload(BaseModel):
    schema_version: int = Field(default=1, description="Schema version of the import file")
    settings: dict[str, Any] = Field(description="Dictionary of category settings to apply")
