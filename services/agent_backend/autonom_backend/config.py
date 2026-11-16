"""Configuration settings for the AUTONOM agent backend."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AUTONOM Agent Backend"
    version: str = "0.1.0"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8765

    # Storage paths
    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    database_filename: str = "autonom.db"

    # CORS origins
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://tauri.localhost",
        "tauri://localhost",
        "https://tauri.localhost",
    ]

    model_config = SettingsConfigDict(env_prefix="AUTONOM_", env_file=".env", extra="ignore")

    @property
    def database_path(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir / self.database_filename


settings = Settings()
