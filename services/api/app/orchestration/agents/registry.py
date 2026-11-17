"""Agent Registry tracking available coordination agents and specialist capabilities."""

import logging
from typing import Any

from app.orchestration.contracts import AgentDefinition

logger = logging.getLogger("autonom.orchestration.agents.registry")


class AgentRegistry:
    """Registry managing available coordination and execution agents in AUTONOM."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        # 1. Five Core Logical Orchestration Agents (Stage 12 active)
        defaults: list[AgentDefinition] = [
            AgentDefinition(
                agent_id="supervisor",
                name="Supervisor Agent",
                role="Workflow Coordinator",
                description="Coordinates multi-agent workflows, lifecycle state transitions, checkpoints, and user governance.",
                capabilities=["workflow_coordination", "state_management", "checkpoint_preservation"],
                supported_task_types=["coordination", "lifecycle"],
                required_permissions=["workflow_control"],
                concurrency_limit=4,
                is_available=True,
                enabled=True,
                implementation_version="1.0.0",
                roadmap_stage="Stage 12 (Active)",
            ),
            AgentDefinition(
                agent_id="planner",
                name="Planning Agent",
                role="Dynamic Workflow Planner",
                description="Decomposes user goals into structured dependency DAGs, enforces cycle detection, and versions plans.",
                capabilities=["goal_decomposition", "dag_generation", "cycle_detection", "plan_versioning"],
                supported_task_types=["planning", "replanning"],
                required_permissions=[],
                concurrency_limit=2,
                is_available=True,
                enabled=True,
                implementation_version="1.0.0",
                roadmap_stage="Stage 12 (Active)",
            ),
            AgentDefinition(
                agent_id="router",
                name="Task Router Agent",
                role="Capability Dispatcher",
                description="Matches workflow step requirements to capable agents, verifies concurrency and permissions with explainability.",
                capabilities=["capability_matching", "concurrency_check", "permission_enforcement", "fallback_routing"],
                supported_task_types=["routing", "dispatch"],
                required_permissions=[],
                concurrency_limit=4,
                is_available=True,
                enabled=True,
                implementation_version="1.0.0",
                roadmap_stage="Stage 12 (Active)",
            ),
            AgentDefinition(
                agent_id="verifier",
                name="Verification Agent",
                role="Multi-Layer Quality Auditor",
                description="Audits step outputs via deterministic schema/type assertions and semantic model evaluations.",
                capabilities=["schema_validation", "deterministic_assertion", "semantic_review", "contract_audit"],
                supported_task_types=["verification", "audit"],
                required_permissions=[],
                concurrency_limit=2,
                is_available=True,
                enabled=True,
                implementation_version="1.0.0",
                roadmap_stage="Stage 12 (Active)",
            ),
            AgentDefinition(
                agent_id="recovery",
                name="Recovery Agent",
                role="Fault Diagnostician & Healer",
                description="Classifies runtime failures across 13 categories, manages bounded retries, and triggers dynamic replanning.",
                capabilities=["failure_classification", "bounded_retry", "dynamic_replanning", "state_recovery"],
                supported_task_types=["recovery", "remediation"],
                required_permissions=["workflow_control"],
                concurrency_limit=2,
                is_available=True,
                enabled=True,
                implementation_version="1.0.0",
                roadmap_stage="Stage 12 (Active)",
            ),
            # 2. General Capability Worker Agent (executes initial safe capabilities)
            AgentDefinition(
                agent_id="capability_worker",
                name="Safe Capability Worker",
                role="Deterministic & AI Capability Executor",
                description="Executes registered capabilities (summarize, classify, extract, diff, transform, validate, inspect).",
                capabilities=[
                    "text_summarize",
                    "text_classify",
                    "structured_extract",
                    "text_compare",
                    "data_transform",
                    "output_validate",
                    "code_inspect",
                ],
                supported_task_types=["execution"],
                required_permissions=[],
                concurrency_limit=4,
                is_available=True,
                enabled=True,
                implementation_version="1.0.0",
                roadmap_stage="Stage 12 (Active)",
            ),
            # 3. Roadmap Specialist Agents (Cataloged for Stage 13+ with honest availability)
            AgentDefinition(
                agent_id="job_search_specialist",
                name="Job Discovery Specialist",
                role="Automated Recruitment Hunter",
                description="Specialized agent for discovering and ranking open opportunities across recruitment platforms.",
                capabilities=["job_discovery", "board_crawling", "opportunity_scoring"],
                supported_task_types=["job_search"],
                concurrency_limit=1,
                is_available=False,
                enabled=False,
                implementation_version="0.0.0",
                roadmap_stage="Stage 14 (Planned)",
            ),
            AgentDefinition(
                agent_id="resume_specialist",
                name="Resume Tailoring Specialist",
                role="Document Synthesis Expert",
                description="Tailors resumes and portfolios to target job descriptions under user authorization.",
                capabilities=["resume_tailoring", "cover_letter_generation", "ats_optimization"],
                supported_task_types=["document_generation"],
                concurrency_limit=1,
                is_available=False,
                enabled=False,
                implementation_version="0.0.0",
                roadmap_stage="Stage 15 (Planned)",
            ),
            AgentDefinition(
                agent_id="browser_specialist",
                name="Browser Automation Specialist",
                role="Web Interaction Operator",
                description="Autonomous web browser driver navigating dynamic job portals and application forms.",
                capabilities=["browser_navigation", "dom_interaction", "form_filling"],
                supported_task_types=["browser_automation"],
                concurrency_limit=1,
                is_available=False,
                enabled=False,
                implementation_version="0.0.0",
                roadmap_stage="Stage 16 (Planned)",
            ),
        ]
        for agent in defaults:
            self.register(agent)

    def register(self, agent: AgentDefinition) -> None:
        """Register an agent definition."""
        self._agents[agent.agent_id] = agent
        logger.debug("Registered agent: %s (%s)", agent.agent_id, agent.name)

    def get(self, agent_id: str) -> AgentDefinition | None:
        """Get agent definition by ID."""
        return self._agents.get(agent_id)

    def list_agents(self, only_available: bool = False) -> list[AgentDefinition]:
        """List all registered agents."""
        agents = list(self._agents.values())
        if only_available:
            return [a for a in agents if a.is_available and a.enabled]
        return agents

    def find_agents_for_capability(self, capability_id: str) -> list[AgentDefinition]:
        """Find available agents capable of executing the specified capability."""
        return [
            a for a in self._agents.values()
            if a.is_available and a.enabled and capability_id in a.capabilities
        ]


# Singleton instance
_agent_registry: AgentRegistry | None = None


def get_agent_registry() -> AgentRegistry:
    """Return shared AgentRegistry singleton."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry
