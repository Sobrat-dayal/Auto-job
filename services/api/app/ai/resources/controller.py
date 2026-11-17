"""Local model lifecycle, VRAM guardrails, and single-active-model scheduling."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from app.ai.contracts import HardwareTelemetry
from app.ai.resources.gpu import get_hardware_telemetry

logger = logging.getLogger("autonom.ai.resources.controller")


class LocalModelResourceController:
    """Enforces the single-active-model rule and memory guardrails for local inference."""

    def __init__(self, max_concurrent_local: int = 1, vram_budget_mb: int = 5000) -> None:
        self.max_concurrent_local = max_concurrent_local
        self.vram_budget_mb = vram_budget_mb
        self._concurrency_semaphore = asyncio.Semaphore(max_concurrent_local)
        self._active_model_lock = asyncio.Lock()
        self._currently_loaded_model: str | None = None
        self._active_inference_count: int = 0

    @property
    def currently_loaded_model(self) -> str | None:
        return self._currently_loaded_model

    @property
    def active_inference_count(self) -> int:
        return self._active_inference_count

    def get_telemetry(self) -> HardwareTelemetry:
        """Returns current hardware telemetry enriched with active local model state."""
        return get_hardware_telemetry(
            active_local_model=self._currently_loaded_model,
            active_inference_count=self._active_inference_count,
        )

    async def ensure_model_ready(
        self,
        target_model_id: str,
        provider_unload_fn: Any = None,
        provider_load_fn: Any = None,
        estimated_vram_mb: int = 4000,
    ) -> None:
        """Enforces single-active-model policy: unloads previous local model before switching."""
        async with self._active_model_lock:
            # 1. Check if model switch is needed
            if self._currently_loaded_model == target_model_id:
                return

            logger.info(
                f"Model switch requested: current='{self._currently_loaded_model}' -> target='{target_model_id}'"
            )

            # 2. Check available VRAM if telemetry is available
            telemetry = self.get_telemetry()
            if telemetry.gpu_vram_available_mb is not None:
                # If switching from an already loaded model, unloading will free memory
                if self._currently_loaded_model is None and telemetry.gpu_vram_available_mb < 1500:
                    logger.warning(
                        f"Low free VRAM: {telemetry.gpu_vram_available_mb} MB available, budget is {self.vram_budget_mb} MB."
                    )

            # 3. If a different model is currently loaded, request unloading
            if self._currently_loaded_model and provider_unload_fn:
                try:
                    logger.info(f"Unloading previous local model '{self._currently_loaded_model}'...")
                    await provider_unload_fn(self._currently_loaded_model)
                    logger.info(f"Successfully unloaded '{self._currently_loaded_model}'.")
                except Exception as exc:
                    logger.warning(f"Error unloading previous model '{self._currently_loaded_model}': {exc}")
                self._currently_loaded_model = None

            # 4. Request loading target model if provider provides explicit load function
            if provider_load_fn:
                try:
                    logger.info(f"Loading target local model '{target_model_id}'...")
                    await provider_load_fn(target_model_id)
                    logger.info(f"Successfully loaded '{target_model_id}'.")
                except Exception as exc:
                    logger.error(f"Failed to load target model '{target_model_id}': {exc}")
                    raise

            self._currently_loaded_model = target_model_id

    @asynccontextmanager
    async def acquire_local_slot(self) -> AsyncIterator[None]:
        """Limits local inference concurrency to the configured maximum (default: 1)."""
        await self._concurrency_semaphore.acquire()
        self._active_inference_count += 1
        try:
            yield
        finally:
            self._active_inference_count = max(0, self._active_inference_count - 1)
            self._concurrency_semaphore.release()

    def set_loaded_model(self, model_id: str | None) -> None:
        """Directly sets or clears currently tracked loaded model identifier."""
        self._currently_loaded_model = model_id


resource_controller = LocalModelResourceController()
