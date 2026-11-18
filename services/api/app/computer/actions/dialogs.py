"""Windows common dialog detection and file path safety enforcement (Stage 17)."""

import logging
import os
from pathlib import Path

logger = logging.getLogger("autonom.computer.actions.dialogs")

# Prohibited destination directories for automated file dialogs
PROHIBITED_DIRECTORIES = {
    os.getenv("WINDIR", "C:\\Windows").lower(),
    os.getenv("PROGRAMFILES", "C:\\Program Files").lower(),
    os.getenv("PROGRAMFILES(X86)", "C:\\Program Files (x86)").lower(),
    os.getenv("SYSTEMROOT", "C:\\Windows").lower(),
}


class FileDialogSafetyGuard:
    """Enforces Stage 14 filesystem boundaries during automated file dialog operations."""

    @staticmethod
    def is_dialog_window(window_class: str) -> bool:
        """Checks if a window class corresponds to a standard Win32 dialog."""
        return window_class in ("#32770", "OperationStatusWindow", "TaskDialog")

    @staticmethod
    def validate_target_file_path(path_str: str) -> tuple[bool, str]:
        """Validates that a requested file path does not violate filesystem security policies."""
        # Check path traversal
        if ".." in path_str:
            return False, "Path traversal sequences ('..') are strictly prohibited"

        try:
            target_path = Path(path_str).resolve()
        except Exception as e:
            return False, f"Invalid path syntax: {e}"

        target_str = str(target_path).lower()

        # Reject prohibited system directories
        for prohibited in PROHIBITED_DIRECTORIES:
            if target_str.startswith(prohibited):
                return False, f"Path violates security policy: writing to {prohibited} is prohibited"

        return True, str(target_path)


dialog_safety_guard = FileDialogSafetyGuard()
