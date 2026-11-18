"""Main Service Facade for the Stage 19 Hybrid Computer Interaction Engine."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Optional
import uuid

from app.hybrid.adapters.registry import InteractionAdapterRegistry, get_adapter_registry
from app.hybrid.contracts import (
    CapabilityProbe,
    HybridActionType,
    HybridDiagnosticsInfo,
    HybridTaskRequest,
    HybridTaskResponse,
    HybridTaskStatus,
    InteractionAction,
    InteractionMethod,
    InteractionObservation,
    InteractionResult,
    InteractionTarget,
    MethodHealthStatus,
    ObservationRequest,
    RoutingDecisionRecordSchema,
)
from app.hybrid.errors import (
    EmergencyStopActiveError,
    NoEligibleMethodError,
    SessionLockedError,
)
from app.hybrid.execution.coordinator import HybridActionCoordinator
from app.hybrid.execution.input_ownership import get_input_coordinator
from app.hybrid.execution.state_machine import HybridStateMachine
from app.hybrid.observations.coordinator import ObservationCoordinator
from app.hybrid.routing.fallback import FallbackController
from app.hybrid.routing.health import MethodHealthTracker
from app.hybrid.routing.router import HybridMethodRouter
from app.hybrid.security.authorization import (
    HybridAuthorizationBridge,
    get_hybrid_auth_bridge,
)
from app.hybrid.security.execution_guard import (
    HybridExecutionGuard,
    get_execution_guard,
)
from app.hybrid.targets.resolver import TargetResolver

logger = logging.getLogger("autonom.hybrid.service")


class HybridComputerService:
    """Central service orchestrating hybrid computer automation across DOM, UIA, Win32, and Visual control."""

    _instance: Optional[HybridComputerService] = None

    @classmethod
    def get_instance(cls) -> HybridComputerService:
        if cls._instance is None:
            cls._instance = HybridComputerService()
        return cls._instance

    def __init__(self) -> None:
        self.registry: InteractionAdapterRegistry = get_adapter_registry()
        self.health_tracker: MethodHealthTracker = MethodHealthTracker()
        self.router: HybridMethodRouter = HybridMethodRouter(
            registry=self.registry,
            health_tracker=self.health_tracker,
        )
        self.fallback_controller: FallbackController = FallbackController()
        self.target_resolver: TargetResolver = TargetResolver()
        self.action_coordinator: HybridActionCoordinator = HybridActionCoordinator(
            registry=self.registry,
            router=self.router,
            fallback_controller=self.fallback_controller,
        )
        self.observation_coordinator: ObservationCoordinator = ObservationCoordinator(
            registry=self.registry,
            router=self.router,
        )
        self.guard: HybridExecutionGuard = get_execution_guard()
        self.auth_bridge: HybridAuthorizationBridge = get_hybrid_auth_bridge()

        # In-memory store for active tasks, routing records, and actions
        self._tasks: dict[str, HybridTaskResponse] = {}
        self._routing_records: dict[str, RoutingDecisionRecordSchema] = {}
        self._action_results: dict[str, InteractionResult] = {}
        self._total_fallbacks: int = 0

    def get_status(self) -> dict[str, Any]:
        """Return engine operational status and available adapters."""
        methods = self.registry.list_methods()
        return {
            "status": "operational",
            "version": "1.0.0",
            "emergency_stop_active": self.guard.is_emergency_stop_active(),
            "session_locked": self.guard.is_session_locked(),
            "methods_available": [m.value for m in methods],
            "total_tasks": len(self._tasks),
            "active_tasks": sum(1 for t in self._tasks.values() if t.status in (HybridTaskStatus.PENDING, HybridTaskStatus.EXECUTING, HybridTaskStatus.ROUTING)),
        }

    def list_methods(self) -> list[InteractionMethod]:
        """List registered method IDs."""
        return self.registry.list_methods()

    def get_capabilities(self) -> list[dict[str, Any]]:
        """Return capability metadata for each registered method."""
        result = []
        for method in self.registry.list_methods():
            adapter = self.registry.get(method)
            health = self.health_tracker.get_status(method)
            result.append({
                "method": method.value,
                "is_healthy": adapter.is_healthy if adapter else False,
                "status": health.status,
                "success_count": health.success_count,
                "failure_count": health.failure_count,
                "avg_latency_ms": health.avg_latency_ms,
            })
        return result

    async def resolve_target(
        self,
        target_hint: Optional[str] = None,
        session_id: Optional[str] = None,
        dom_selector: Optional[str] = None,
        window_title: Optional[str] = None,
        window_handle: Optional[int] = None,
        coordinates: Optional[dict[str, Any]] = None,
        process_name: Optional[str] = None,
    ) -> InteractionTarget:
        """Resolve target metadata into an InteractionTarget."""
        return await self.target_resolver.resolve(
            target_hint=target_hint,
            session_id=session_id,
            dom_selector=dom_selector,
            window_title=window_title,
            window_handle=window_handle,
            coordinates=coordinates,
            process_name=process_name,
        )

    async def probe_methods(self, target: InteractionTarget) -> dict[str, CapabilityProbe]:
        """Probe all adapters against a target surface."""
        probes = await self.registry.probe_all(target)
        return {m.value: probe for m, probe in probes.items()}

    async def preview_route(
        self,
        target: InteractionTarget,
        action_type: Optional[HybridActionType] = None,
        preferred_method: Optional[InteractionMethod] = None,
    ) -> RoutingDecisionRecordSchema:
        """Simulate and preview method routing without executing actions."""
        _, decision = await self.router.route(
            target=target,
            action_type=action_type,
            preferred_method=preferred_method,
        )
        return decision

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Capture observation across the target surface."""
        self.guard.ensure_execution_allowed()
        return await self.observation_coordinator.observe(request)

    async def execute_action(self, action: InteractionAction) -> InteractionResult:
        """Execute a single unified action."""
        self.guard.ensure_execution_allowed()

        result, routing_rec, attempts = await self.action_coordinator.execute_action(action)
        self._action_results[action.action_id] = result
        if routing_rec:
            self._routing_records[routing_rec.decision_id] = routing_rec
        if result.fallback_occurred:
            self._total_fallbacks += 1

        return result

    def get_action(self, action_id: str) -> Optional[InteractionResult]:
        """Retrieve past action result."""
        return self._action_results.get(action_id)

    async def submit_task(self, request: HybridTaskRequest) -> HybridTaskResponse:
        """Submit a multi-step or single-step hybrid computer automation task."""
        self.guard.ensure_execution_allowed()

        task_id = f"htask_{uuid.uuid4().hex[:12]}"
        sm = HybridStateMachine(initial_status=HybridTaskStatus.PENDING)

        # Resolve or prepare target
        target = request.target
        if not target:
            target = await self.target_resolver.resolve(target_hint=request.instruction)

        sm.transition_to(HybridTaskStatus.ROUTING)

        # Route optimal method
        selected_method, routing_decision = await self.router.route(
            target=target,
            action_type=request.action_type or HybridActionType.CLICK,
            preferred_method=request.preferred_method,
            task_id=task_id,
        )
        self._routing_records[routing_decision.decision_id] = routing_decision

        sm.transition_to(HybridTaskStatus.EXECUTING)

        # Construct interaction action
        action = InteractionAction(
            task_id=task_id,
            target=target,
            action_type=request.action_type or HybridActionType.CLICK,
            method=selected_method,
            allow_fallback=request.allow_fallback,
        )

        result, _, attempts = await self.action_coordinator.execute_action(action)
        if result.fallback_occurred:
            self._total_fallbacks += 1

        final_status = HybridTaskStatus.COMPLETED if result.success else HybridTaskStatus.FAILED

        response = HybridTaskResponse(
            task_id=task_id,
            status=final_status,
            instruction=request.instruction,
            selected_method=result.method,
            routing_decision=routing_decision,
            attempts=attempts,
            final_result=result,
            error_message=result.error_message,
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        self._tasks[task_id] = response
        return response

    def get_task(self, task_id: str) -> Optional[HybridTaskResponse]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 50) -> list[HybridTaskResponse]:
        """List recent hybrid tasks."""
        return list(self._tasks.values())[-limit:]

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        task = self._tasks.get(task_id)
        if task and task.status in (HybridTaskStatus.PENDING, HybridTaskStatus.ROUTING, HybridTaskStatus.EXECUTING):
            task.status = HybridTaskStatus.CANCELLED
            return True
        return False

    def get_diagnostics(self) -> HybridDiagnosticsInfo:
        """Return comprehensive diagnostics."""
        input_owner = get_input_coordinator().current_owner
        return HybridDiagnosticsInfo(
            engine_version="1.0.0",
            is_healthy=True,
            emergency_stop_active=self.guard.is_emergency_stop_active(),
            input_lease_owner=input_owner,
            methods=self.health_tracker.list_all(),
            total_tasks=len(self._tasks),
            active_tasks=sum(1 for t in self._tasks.values() if t.status in (HybridTaskStatus.PENDING, HybridTaskStatus.EXECUTING, HybridTaskStatus.ROUTING)),
            total_fallbacks=self._total_fallbacks,
            recent_routing_decisions=list(self._routing_records.values())[-10:],
        )

    async def activate_killswitch(self, reason: str = "Operator hybrid emergency stop") -> None:
        """Trigger emergency stop."""
        await self.guard.activate_killswitch(reason=reason)

    async def deactivate_killswitch(self) -> None:
        """Reset emergency stop."""
        await self.guard.deactivate_killswitch()


# Global singleton instance
hybrid_computer_service: HybridComputerService = HybridComputerService.get_instance()
