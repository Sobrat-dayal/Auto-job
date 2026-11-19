"""Platform module for Stage 30 Recruitment Monitoring."""

from app.recruitment.monitoring.platform.windows_lifecycle import (
    WindowsLifecycleManager,
    windows_lifecycle,
)

__all__ = ["WindowsLifecycleManager", "windows_lifecycle"]
