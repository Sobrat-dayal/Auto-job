"""System telemetry and hardware metric endpoints."""

import sys
import platform
import psutil
from fastapi import APIRouter

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("")
async def get_system_telemetry():
    """Returns real-time hardware telemetry and operating system information."""
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    proc = psutil.Process()
    proc_mem = proc.memory_info()

    return {
        "os": f"Windows {platform.release()}" if platform.system() == "Windows" else platform.system(),
        "platform": sys.platform,
        "python_version": platform.python_version(),
        "cpu_usage_percent": cpu_percent,
        "memory": {
            "total_mb": round(mem.total / (1024 * 1024), 1),
            "available_mb": round(mem.available / (1024 * 1024), 1),
            "process_rss_mb": round(proc_mem.rss / (1024 * 1024), 1),
        },
        "monitors": [
            {
                "index": 0,
                "width": 1920,
                "height": 1080,
                "scale_factor": 1.0,
                "is_primary": True,
            }
        ],
    }
