"""Host hardware telemetry provider: CPU, RAM, and NVIDIA RTX 4050 GPU VRAM metrics."""

import logging
import time

import psutil

from app.ai.contracts import HardwareTelemetry

logger = logging.getLogger("autonom.ai.resources.gpu")

# Module-level cache for throttling telemetry queries (2.0s TTL)
_cached_telemetry: HardwareTelemetry | None = None
_last_telemetry_time: float = 0.0


def get_hardware_telemetry(active_local_model: str | None = None, active_inference_count: int = 0) -> HardwareTelemetry:
    """Collects real-time hardware telemetry: RAM, CPU, and NVIDIA VRAM."""
    global _cached_telemetry, _last_telemetry_time

    now = time.time()
    if _cached_telemetry is not None and (now - _last_telemetry_time) < 2.0:
        # Return copy with updated active model/inference count
        return _cached_telemetry.model_copy(
            update={
                "active_local_model": active_local_model,
                "active_inference_count": active_inference_count,
            }
        )

    # 1. System RAM
    vm = psutil.virtual_memory()
    ram_total_mb = int(vm.total / (1024 * 1024))
    ram_avail_mb = int(vm.available / (1024 * 1024))
    ram_used_mb = int(vm.used / (1024 * 1024))
    ram_percent = round(vm.percent, 1)

    # 2. NVIDIA GPU VRAM via NVML
    gpu_name: str | None = None
    gpu_total_mb: int | None = None
    gpu_used_mb: int | None = None
    gpu_avail_mb: int | None = None
    gpu_percent: float | None = None

    try:
        import pynvml

        pynvml.nvmlInit()
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name_raw = pynvml.nvmlDeviceGetName(handle)
                gpu_name = name_raw if isinstance(name_raw, str) else name_raw.decode("utf-8")
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_total_mb = int(mem_info.total / (1024 * 1024))
                gpu_used_mb = int(mem_info.used / (1024 * 1024))
                gpu_avail_mb = int(mem_info.free / (1024 * 1024))
                gpu_percent = round((gpu_used_mb / gpu_total_mb) * 100.0, 1) if gpu_total_mb > 0 else 0.0
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
    except Exception as exc:
        logger.debug(f"NVML GPU telemetry query skipped or unavailable: {exc}")

    telemetry = HardwareTelemetry(
        system_ram_total_mb=ram_total_mb,
        system_ram_available_mb=ram_avail_mb,
        system_ram_used_mb=ram_used_mb,
        system_ram_percent=ram_percent,
        gpu_name=gpu_name,
        gpu_vram_total_mb=gpu_total_mb,
        gpu_vram_used_mb=gpu_used_mb,
        gpu_vram_available_mb=gpu_avail_mb,
        gpu_vram_percent=gpu_percent,
        active_local_model=active_local_model,
        active_inference_count=active_inference_count,
        local_concurrency_limit=1,
    )

    _cached_telemetry = telemetry
    _last_telemetry_time = now
    return telemetry
