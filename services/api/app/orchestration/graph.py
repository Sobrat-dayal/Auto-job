"""Dependency Graph (DAG) engine for workflow step execution and validation."""

from collections import defaultdict, deque
from typing import Any

from app.orchestration.contracts import StepStatus, WorkflowStepDefinition


class DependencyGraph:
    """Directed Acyclic Graph (DAG) representation of workflow steps.

    Provides topological sorting, cycle detection, executable step identification,
    and parallel stage computation.
    """

    def __init__(self, steps: list[WorkflowStepDefinition]) -> None:
        self.steps: dict[str, WorkflowStepDefinition] = {step.step_id: step for step in steps}
        self.step_ids: list[str] = [step.step_id for step in steps]
        # in_edges: step_id -> list of steps it depends on (predecessors)
        self.dependencies: dict[str, set[str]] = {}
        # out_edges: step_id -> list of steps that depend on it (successors)
        self.dependents: dict[str, set[str]] = defaultdict(set)

        self._build_graph()
        self._validate_dependencies()
        self._topological_order = self._compute_topological_sort()

    def _build_graph(self) -> None:
        for step_id, step in self.steps.items():
            deps = set(step.dependencies)
            self.dependencies[step_id] = deps
            for dep in deps:
                self.dependents[dep].add(step_id)

    def _validate_dependencies(self) -> None:
        """Validate that all referenced dependencies exist in the step registry."""
        for step_id, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.steps:
                    raise ValueError(
                        f"Step '{step_id}' references unknown dependency '{dep}'"
                    )
                if dep == step_id:
                    raise ValueError(f"Step '{step_id}' cannot depend on itself (self-cycle)")

    def _compute_topological_sort(self) -> list[str]:
        """Compute topological sort using Kahn's algorithm; detect cycles fast."""
        in_degree: dict[str, int] = {
            step_id: len(deps) for step_id, deps in self.dependencies.items()
        }
        queue: deque[str] = deque([
            step_id for step_id, deg in in_degree.items() if deg == 0
        ])
        ordered: list[str] = []

        while queue:
            curr = queue.popleft()
            ordered.append(curr)
            for succ in self.dependents[curr]:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        if len(ordered) != len(self.steps):
            cycle_steps = [s for s, deg in in_degree.items() if deg > 0]
            raise ValueError(
                f"Cyclic dependency detected in workflow plan involving steps: {cycle_steps}"
            )

        return ordered

    @property
    def topological_order(self) -> list[str]:
        """Return the steps in topological order."""
        return list(self._topological_order)

    def get_root_steps(self) -> list[str]:
        """Return steps that have zero dependencies (can start immediately)."""
        return [step_id for step_id, deps in self.dependencies.items() if len(deps) == 0]

    def get_leaf_steps(self) -> list[str]:
        """Return steps that have no dependent successors."""
        return [step_id for step_id in self.steps if len(self.dependents[step_id]) == 0]

    def get_successors(self, step_id: str) -> set[str]:
        """Return direct dependent step IDs."""
        return set(self.dependents.get(step_id, set()))

    def get_all_downstream(self, step_id: str) -> set[str]:
        """Return all downstream dependent steps (transitive closure)."""
        downstream: set[str] = set()
        queue: deque[str] = deque(self.dependents.get(step_id, set()))
        while queue:
            curr = queue.popleft()
            if curr not in downstream:
                downstream.add(curr)
                queue.extend(self.dependents.get(curr, set()))
        return downstream

    def get_executable_steps(
        self,
        step_statuses: dict[str, StepStatus],
    ) -> list[str]:
        """Return step IDs that are ready to execute.

        A step is executable if:
        1. It is currently in PENDING or READY status.
        2. All of its dependencies have COMPLETED status.
        """
        executable: list[str] = []
        for step_id in self._topological_order:
            status = step_statuses.get(step_id, StepStatus.PENDING)
            if status not in (StepStatus.PENDING, StepStatus.READY):
                continue

            deps = self.dependencies.get(step_id, set())
            deps_completed = all(
                step_statuses.get(dep) == StepStatus.COMPLETED for dep in deps
            )
            if deps_completed:
                executable.append(step_id)

        return executable

    def compute_parallel_stages(self) -> list[list[str]]:
        """Compute execution tiers/stages where all steps in a tier can run concurrently."""
        levels: dict[str, int] = {}
        for step_id in self._topological_order:
            deps = self.dependencies.get(step_id, set())
            if not deps:
                levels[step_id] = 0
            else:
                levels[step_id] = max(levels[d] for d in deps) + 1

        max_level = max(levels.values()) if levels else 0
        stages: list[list[str]] = [[] for _ in range(max_level + 1)]
        for step_id, lvl in levels.items():
            stages[lvl].append(step_id)

        return stages

    def to_dict(self) -> dict[str, Any]:
        """Export graph metadata for visualization and serialization."""
        return {
            "steps": [
                {
                    "step_id": s.step_id,
                    "title": s.title,
                    "capability_id": s.capability_id,
                    "dependencies": list(s.dependencies),
                }
                for s in self.steps.values()
            ],
            "topological_order": self.topological_order,
            "stages": self.compute_parallel_stages(),
        }
