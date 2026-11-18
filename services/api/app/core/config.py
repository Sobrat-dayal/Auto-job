"""Application configuration settings for AUTONOM API."""

import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_data_dir() -> Path:
    """Resolves local data directory following Windows %LOCALAPPDATA%/AUTONOM conventions."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "AUTONOM"
    return Path.home() / ".autonom"


class Settings(BaseSettings):
    app_name: str = "AUTONOM API"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    host: str = Field(default="127.0.0.1", description="Host to bind service to")
    port: int = Field(default=8765, description="Port to bind service to")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")

    # Local API Security
    api_key: str = Field(
        default="dev-local-autonom-key",
        description="Local API token for authenticated endpoints",
    )

    # Task Execution & Workers
    max_concurrent_workers: int = Field(default=4, description="Maximum concurrent asynchronous task workers")
    max_queued_tasks: int = Field(default=50, description="Maximum bounded queue capacity for pending tasks")
    task_default_timeout_seconds: float = Field(default=60.0, description="Default task execution timeout in seconds")

    # Real-time Events
    event_buffer_size: int = Field(default=200, description="Maximum in-memory events retained in ring buffer")

    # Local storage & Database
    data_dir: Path = Field(
        default_factory=default_data_dir,
        description="Root application data directory (Windows %LOCALAPPDATA%/AUTONOM)",
    )
    database_busy_timeout_ms: int = Field(default=10000, description="SQLite busy timeout in milliseconds")
    backup_retention_count: int = Field(default=10, description="Number of database backups to retain")
    data_retention_days: int = Field(default=90, description="Default retention days for transient diagnostic records")

    # CORS origins
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "http://tauri.localhost",
        "tauri://localhost",
        "https://tauri.localhost",
    ]

    model_config = SettingsConfigDict(
        env_prefix="AUTONOM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError(f"Port must be between 1024 and 65535, got {v}")
        return v

    @property
    def is_loopback(self) -> bool:
        return self.host in ("127.0.0.1", "localhost", "::1")

    @property
    def database_dir(self) -> Path:
        return self.data_dir / "database"

    @property
    def database_path(self) -> Path:
        return self.database_dir / "autonom.db"

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.database_path.as_posix()}"

    @property
    def artifacts_dir(self) -> Path:
        return self.data_dir / "artifacts"

    @property
    def backups_dir(self) -> Path:
        return self.data_dir / "backups"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def config_dir(self) -> Path:
        return self.data_dir / "config"

    @property
    def browser_downloads_dir(self) -> Path:
        return self.artifacts_dir / "browser_downloads"

    @property
    def browser_screenshots_dir(self) -> Path:
        return self.artifacts_dir / "browser_screenshots"

    @property
    def browser_profiles_dir(self) -> Path:
        return self.data_dir / "browser_profiles"

    @property
    def browser_traces_dir(self) -> Path:
        return self.data_dir / "browser_traces"

    def ensure_directories(self) -> None:
        """Creates the full application directory layout if missing."""
        for d in (
            self.database_dir,
            self.artifacts_dir / "resumes",
            self.artifacts_dir / "documents",
            self.artifacts_dir / "reports",
            self.artifacts_dir / "generated",
            self.browser_downloads_dir,
            self.browser_screenshots_dir,
            self.browser_profiles_dir,
            self.browser_traces_dir,
            self.backups_dir,
            self.logs_dir,
            self.cache_dir,
            self.config_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
