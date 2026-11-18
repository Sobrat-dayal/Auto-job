"""Windows process enumeration and discovery (Stage 17)."""

from datetime import UTC, datetime
import logging
import psutil

from app.computer.contracts import DesktopApplicationInfo
from app.computer.windows.identity import process_identity_validator

logger = logging.getLogger("autonom.computer.windows.processes")


class ProcessDiscoveryManager:
    """Discovers and catalogs running applications and processes on Windows."""

    SYSTEM_PROCESS_NAMES = {
        "system idle process",
        "system",
        "registry",
        "smss.exe",
        "csrss.exe",
        "wininit.exe",
        "services.exe",
        "lsass.exe",
        "svchost.exe",
        "fontdrvhost.exe",
        "dwm.exe",
        "spoolsv.exe",
    }

    def list_running_applications(self) -> list[DesktopApplicationInfo]:
        """Discovers interactive applications grouped by executable name."""
        apps_by_name: dict[str, DesktopApplicationInfo] = {}

        for proc in psutil.process_iter(["pid", "name", "exe", "create_time"]):
            try:
                name = proc.info["name"] or ""
                if not name or name.lower() in self.SYSTEM_PROCESS_NAMES:
                    continue

                exe_path = proc.info.get("exe") or ""
                pid = proc.info["pid"]

                app_key = name.lower()
                if app_key not in apps_by_name:
                    display_name = name.rsplit(".", 1)[0].replace("_", " ").title()
                    integrity = process_identity_validator.get_process_integrity_level(pid)
                    risk_level = "HIGH" if integrity in ("high", "system") else "LOW"

                    app_id = f"app_{name.lower().replace('.', '_')}"
                    apps_by_name[app_key] = DesktopApplicationInfo(
                        id=app_id,
                        name=display_name,
                        executable_path=exe_path or name,
                        executable_name=name,
                        publisher="Microsoft Corporation" if "windows" in exe_path.lower() else "Verified Local",
                        is_allowed=True,
                        risk_level=risk_level,
                        integrity_level=integrity,
                        pids=[pid],
                        window_count=0,
                        last_detected_at=datetime.now(UTC),
                    )
                else:
                    apps_by_name[app_key].pids.append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return list(apps_by_name.values())


process_discovery_manager = ProcessDiscoveryManager()
