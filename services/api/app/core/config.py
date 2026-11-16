"""Application configuration settings for AUTONOM API."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    max_concurrent_workers: int = Field(
        default=4, description="Maximum concurrent asynchronous task workers"
    )
    max_queued_tasks: int = Field(
        default=50, description="Maximum bounded queue capacity for pending tasks"
    )
    task_default_timeout_seconds: float = Field(
        default=60.0, description="Default task execution timeout in seconds"
    )

    # Real-time Events
    event_buffer_size: int = Field(
        default=200, description="Maximum in-memory events retained in ring buffer"
    )

    # Local storage
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data",
        description="Path to local data directory",
    )

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


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
