"""Stage 14 authorization integration and application allowlist validation (Stage 17)."""

import logging
from app.computer.windows.identity import process_identity_validator

logger = logging.getLogger("autonom.computer.security.authorization")

# Applications allowed for automation in standard policy
DEFAULT_ALLOWED_APPS = {
    "notepad.exe",
    "calc.exe",
    "calculator.exe",
    "calculatorapp.exe",
    "explorer.exe",
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "windowsterminal.exe",
    "code.exe",
    "autonom.exe",
    "python.exe",
    "pythonw.exe",
}


class DesktopAuthorizationPolicy:
    """Enforces application allowlists and process integrity boundaries."""

    def __init__(self) -> None:
        self.allowed_executables = set(DEFAULT_ALLOWED_APPS)

    def is_application_allowed(self, executable_name: str) -> bool:
        """Checks if executable name is on the approved desktop automation allowlist."""
        return executable_name.lower() in self.allowed_executables

    def validate_process_for_automation(self, pid: int, process_name: str) -> tuple[bool, str]:
        """Validates that a process is allowed and not running in an elevated integrity context without clearance."""
        if not self.is_application_allowed(process_name):
            return False, f"Application '{process_name}' is not in the approved desktop automation allowlist"

        if process_identity_validator.is_elevated_process(pid):
            return False, f"Process '{process_name}' (PID {pid}) runs with High/System integrity and cannot be automated from standard user context"

        return True, "Authorized"


desktop_auth_policy = DesktopAuthorizationPolicy()
