"""Agent Registry tracking all 24 autonomous coordination and specialist execution agents."""

from datetime import UTC, datetime
import logging
from typing import Any

from app.orchestration.agents.contracts import (
    AgentCategory,
    AgentConfigurationUpdate,
    AgentManifest,
    AgentStatusResponse,
    AvailabilityState,
)
from app.orchestration.agents.manifests import build_default_manifests, validate_manifest
from app.orchestration.contracts import AgentDefinition

logger = logging.getLogger("autonom.orchestration.agents.registry")


def manifest_to_definition(m: AgentManifest) -> AgentDefinition:
    """Convert an AgentManifest to backward-compatible AgentDefinition schema."""
    return AgentDefinition(
        agent_id=m.agent_id,
        name=m.name,
        role=m.role,
        description=m.description,
        capabilities=list(m.capabilities),
        supported_task_types=[m.category.value, "execution"],
        required_permissions=list(m.required_permissions),
        concurrency_limit=m.execution_limits.concurrency_limit,
        model_preference=m.model_profile.preferred_model,
        is_available=m.is_available,
        enabled=m.enabled,
        implementation_version=m.version,
        roadmap_stage=m.roadmap_stage,
    )


class AgentRegistry:
    """Central registry managing manifests, configurations, and lifecycle for all agents."""

    def __init__(self) -> None:
        self._manifests: dict[str, AgentManifest] = {}
        self._definitions: dict[str, AgentDefinition] = {}
        # Track runtime execution stats per agent
        self._stats: dict[str, dict[str, Any]] = {}
        self._active_assignments: dict[str, int] = {}
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        """Register the 24 standard AUTONOM agents (5 Core + 19 Specialists)."""
        defaults = build_default_manifests()
        for manifest in defaults:
            self.register(manifest)

        # Backward compatibility alias for Stage 12 test expectations
        self._definitions["job_search_specialist"] = AgentDefinition(
            agent_id="job_search_specialist",
            name="Job Discovery Specialist (Legacy)",
            role="Recruitment Opportunity Explorer",
            description="Legacy alias for job_discovery_agent",
            capabilities=["job_discovery", "board_crawling"],
            supported_task_types=["job_search"],
            concurrency_limit=1,
            is_available=False,
            enabled=False,
            implementation_version="0.0.0",
            roadmap_stage="Stage 14 (Planned)",
        )

    def register(self, manifest: AgentManifest) -> None:
        """Register or update an agent manifest with validation."""
        errors = validate_manifest(manifest)
        if errors:
            raise ValueError(f"Invalid AgentManifest '{manifest.agent_id}': {', '.join(errors)}")

        self._manifests[manifest.agent_id] = manifest
        self._definitions[manifest.agent_id] = manifest_to_definition(manifest)
        if manifest.agent_id not in self._stats:
            self._stats[manifest.agent_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "last_execution_at": None,
            }
        logger.debug("Registered agent manifest: %s (%s)", manifest.agent_id, manifest.name)

    def get_manifest(self, agent_id: str) -> AgentManifest | None:
        """Get agent manifest by ID."""
        return self._manifests.get(agent_id)

    def get(self, agent_id: str) -> AgentDefinition | None:
        """Get agent definition by ID (backward-compatible)."""
        return self._definitions.get(agent_id)

    def list_manifests(
        self,
        category: str | None = None,
        status: str | None = None,
        only_available: bool = False,
    ) -> list[AgentManifest]:
        """List manifests with optional category, status, and availability filtering."""
        manifests = list(self._manifests.values())

        if category:
            manifests = [m for m in manifests if m.category.value == category]

        if status:
            manifests = [m for m in manifests if m.availability_state.value == status]

        if only_available:
            manifests = [m for m in manifests if m.is_available]

        return manifests

    def list_agents(self, only_available: bool = False) -> list[AgentDefinition]:
        """List agent definitions (backward-compatible)."""
        defs = list(self._definitions.values())
        if only_available:
            return [d for d in defs if d.is_available and d.enabled]
        return defs

    def find_agents_for_capability(self, capability_id: str) -> list[AgentDefinition]:
        """Find capable agents (backward-compatible for TaskRouter)."""
        return [
            d for d in self._definitions.values()
            if d.is_available and d.enabled and capability_id in d.capabilities
        ]

    def find_manifests_for_capability(self, capability_id: str) -> list[AgentManifest]:
        """Find capable agent manifests."""
        return [
            m for m in self._manifests.values()
            if m.is_available and capability_id in m.capabilities
        ]

    def update_configuration(self, agent_id: str, update: AgentConfigurationUpdate) -> AgentManifest:
        """Apply permitted configuration updates to an agent manifest."""
        manifest = self.get_manifest(agent_id)
        if not manifest:
            raise KeyError(f"Agent '{agent_id}' not found")

        # Mutate in-place safely
        if update.enabled is not None:
            manifest.enabled = update.enabled
        if update.preferred_model is not None:
            manifest.model_profile.preferred_model = update.preferred_model
        if update.concurrency_limit is not None:
            manifest.execution_limits.concurrency_limit = update.concurrency_limit
        if update.timeout_seconds is not None:
            manifest.execution_limits.timeout_seconds = update.timeout_seconds
        if update.temperature is not None:
            manifest.model_profile.temperature = update.temperature
        if update.max_tokens is not None:
            manifest.model_profile.max_output_tokens = update.max_tokens
        if update.local_first is not None:
            manifest.model_profile.local_first = update.local_first
        if update.cloud_permitted is not None:
            manifest.model_profile.cloud_permitted = update.cloud_permitted
        if update.allowed_capabilities is not None:
            manifest.capabilities = update.allowed_capabilities

        # Update definition cache
        self._definitions[agent_id] = manifest_to_definition(manifest)
        logger.info("Updated configuration for agent '%s'", agent_id)
        return manifest

    def record_execution_telemetry(
        self,
        agent_id: str,
        status: str,
        duration_ms: int = 0,
        model_used: str | None = None,
    ) -> None:
        """Record runtime telemetry for an agent execution."""
        if agent_id not in self._stats:
            self._stats[agent_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "last_execution_at": None,
            }
        stats = self._stats[agent_id]
        stats["total_executions"] += 1
        if status == "completed":
            stats["successful_executions"] += 1
        elif status == "failed":
            stats["failed_executions"] += 1
        stats["last_execution_at"] = datetime.now(UTC)

    def get_agent_status(
        self,
        agent_id: str,
        active_counts: dict[str, int] | None = None,
    ) -> AgentStatusResponse:
        """Retrieve live operational status and assignment metrics for an agent."""
        manifest = self.get_manifest(agent_id)
        if not manifest:
            raise KeyError(f"Agent '{agent_id}' not found")

        counts = active_counts or self._active_assignments
        active = counts.get(agent_id, 0)
        limit = manifest.execution_limits.concurrency_limit
        stats = self._stats.get(agent_id, {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "last_execution_at": None,
        })

        return AgentStatusResponse(
            agent_id=agent_id,
            name=manifest.name,
            category=manifest.category,
            availability_state=manifest.availability_state,
            enabled=manifest.enabled,
            active_assignments=active,
            concurrency_limit=limit,
            is_busy=active >= limit,
            preferred_model=manifest.model_profile.preferred_model,
            total_executions=stats["total_executions"],
            successful_executions=stats["successful_executions"],
            failed_executions=stats["failed_executions"],
            last_execution_at=stats["last_execution_at"],
        )

    def run_diagnostic_test(self, agent_id: str) -> dict[str, Any]:
        """Execute a safe, isolated self-diagnostic test for the specified agent."""
        manifest = self.get_manifest(agent_id)
        if not manifest:
            raise KeyError(f"Agent '{agent_id}' not found")

        start = datetime.now(UTC)
        test_passed = manifest.is_available and len(manifest.capabilities) > 0
        details = (
            f"Diagnostic check for '{manifest.name}': manifest valid, "
            f"availability='{manifest.availability_state.value}', "
            f"{len(manifest.capabilities)} capabilities declared."
        )

        return {
            "agent_id": agent_id,
            "agent_name": manifest.name,
            "passed": test_passed,
            "availability": manifest.availability_state.value,
            "capabilities_verified": manifest.capabilities,
            "duration_ms": int((datetime.now(UTC) - start).total_seconds() * 1000),
            "details": details,
            "tested_at": start.isoformat(),
        }


# Global singleton instance
_agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Return shared AgentRegistry singleton."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry
