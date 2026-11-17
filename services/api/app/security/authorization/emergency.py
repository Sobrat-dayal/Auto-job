"""Emergency Stop Controller managing global emergency stop and automation pause."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Optional

from app.db.engine import get_db_session
from app.repositories.authorization_repository import AuthorizationRepository
from app.security.authorization.contracts import EmergencyStopState

logger = logging.getLogger("autonom.security.emergency")


class EmergencyStopController:
    """Manages global emergency stop and automation pause with fast in-memory checks and persistent backing."""

    _instance: Optional["EmergencyStopController"] = None

    def __init__(self) -> None:
        self._is_emergency_stop_active: bool = False
        self._is_automation_paused: bool = False
        self._activated_at: Optional[datetime] = None
        self._activated_by: Optional[str] = None
        self._reason: Optional[str] = None
        self._paused_at: Optional[datetime] = None
        self._paused_by: Optional[str] = None
        self._pause_reason: Optional[str] = None
        self._lock = asyncio.Lock()
        self._initialized: bool = False

    @classmethod
    def get_instance(cls) -> "EmergencyStopController":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def is_emergency_stop_active(self) -> bool:
        return self._is_emergency_stop_active

    @property
    def is_automation_paused(self) -> bool:
        return self._is_automation_paused or self._is_emergency_stop_active

    async def initialize(self) -> None:
        """Loads persistent emergency stop state from database on backend startup."""
        async with self._lock:
            if self._initialized:
                return
            try:
                async with get_db_session() as session:
                    repo = AuthorizationRepository(session)
                    state = await repo.get_emergency_stop_state()
                    self._is_emergency_stop_active = state.is_emergency_stop_active
                    self._activated_at = state.emergency_stop_activated_at
                    self._activated_by = state.emergency_stop_activated_by
                    self._reason = state.emergency_stop_reason
                    self._is_automation_paused = state.is_automation_paused
                    self._paused_at = state.automation_paused_at
                    self._paused_by = state.automation_paused_by
                    self._pause_reason = state.automation_pause_reason
                    self._initialized = True
                    logger.info(
                        "EmergencyStopController initialized: emergency_stop=%s, automation_paused=%s",
                        self._is_emergency_stop_active,
                        self._is_automation_paused,
                    )
            except Exception as e:
                logger.error("Failed to load emergency stop state from database, failing closed: %s", e)
                # Fail-closed: assume emergency stop might be active if DB check fails
                self._initialized = True

    async def activate_emergency_stop(
        self,
        activated_by: str = "user",
        reason: str | None = None,
    ) -> EmergencyStopState:
        """Immediately activates emergency stop and persists state."""
        async with self._lock:
            self._is_emergency_stop_active = True
            now = datetime.now(UTC)
            self._activated_at = now
            self._activated_by = activated_by
            self._reason = reason or "Emergency Stop triggered by user"

            try:
                async with get_db_session() as session:
                    repo = AuthorizationRepository(session)
                    await repo.set_emergency_stop(active=True, activated_by=activated_by, reason=self._reason)
            except Exception as e:
                logger.error("Failed to persist emergency stop state: %s", e)

            logger.critical("EMERGENCY STOP ACTIVATED by '%s': %s", activated_by, self._reason)
            return self.get_state()

    async def clear_emergency_stop(
        self,
        cleared_by: str = "user",
    ) -> EmergencyStopState:
        """Clears emergency stop following explicit user confirmation."""
        async with self._lock:
            self._is_emergency_stop_active = False
            self._activated_at = None
            self._activated_by = None
            self._reason = None

            try:
                async with get_db_session() as session:
                    repo = AuthorizationRepository(session)
                    await repo.set_emergency_stop(active=False, activated_by=cleared_by, reason=None)
            except Exception as e:
                logger.error("Failed to persist emergency stop clear: %s", e)

            logger.info("Emergency Stop cleared by '%s'", cleared_by)
            return self.get_state()

    async def pause_automation(
        self,
        paused_by: str = "user",
        reason: str | None = None,
    ) -> EmergencyStopState:
        """Pauses autonomous background dispatching."""
        async with self._lock:
            self._is_automation_paused = True
            now = datetime.now(UTC)
            self._paused_at = now
            self._paused_by = paused_by
            self._pause_reason = reason or "Automation paused by user"

            try:
                async with get_db_session() as session:
                    repo = AuthorizationRepository(session)
                    await repo.set_automation_pause(paused=True, paused_by=paused_by, reason=self._pause_reason)
            except Exception as e:
                logger.error("Failed to persist automation pause: %s", e)

            logger.info("Automation dispatch PAUSED by '%s'", paused_by)
            return self.get_state()

    async def resume_automation(
        self,
        resumed_by: str = "user",
    ) -> EmergencyStopState:
        """Resumes autonomous background dispatching."""
        async with self._lock:
            self._is_automation_paused = False
            self._paused_at = None
            self._paused_by = None
            self._pause_reason = None

            try:
                async with get_db_session() as session:
                    repo = AuthorizationRepository(session)
                    await repo.set_automation_pause(paused=False, paused_by=resumed_by, reason=None)
            except Exception as e:
                logger.error("Failed to persist automation resume: %s", e)

            logger.info("Automation dispatch RESUMED by '%s'", resumed_by)
            return self.get_state()

    def get_state(self) -> EmergencyStopState:
        """Returns snapshot of current emergency and pause state."""
        return EmergencyStopState(
            is_emergency_stop_active=self._is_emergency_stop_active,
            emergency_stop_activated_at=self._activated_at,
            emergency_stop_activated_by=self._activated_by,
            emergency_stop_reason=self._reason,
            is_automation_paused=self._is_automation_paused,
            automation_paused_at=self._paused_at,
            automation_paused_by=self._paused_by,
            automation_pause_reason=self._pause_reason,
            updated_at=datetime.now(UTC),
        )


def get_emergency_stop_controller() -> EmergencyStopController:
    """Returns the singleton EmergencyStopController instance."""
    return EmergencyStopController.get_instance()
