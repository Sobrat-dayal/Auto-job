"""Boolean logic evaluation (AND, OR, AtLeastN) and unknown propagation for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from typing import Any
from app.recruitment.matching.contracts import (
    GroupEvaluationResult,
    RequirementEvaluationResult,
    RequirementMatchCategory,
)

logger = logging.getLogger("autonom.recruitment.matching.eligibility.logical_groups")


def evaluate_logical_groups(
    groups: list[dict[str, Any]],
    atomic_results: list[RequirementEvaluationResult],
) -> list[GroupEvaluationResult]:
    """Evaluates nested logical requirement groups adhering to 3-valued logic (Section 20-25)."""
    results: list[GroupEvaluationResult] = []

    # Map atomic results by name/id
    res_map: dict[str, RequirementEvaluationResult] = {}
    for r in atomic_results:
        res_map[r.requirement_id.lower()] = r
        res_map[r.name.lower()] = r

    for g in groups:
        g_id = g.get("id", "group_default")
        op = g.get("operator", "AND").upper()
        child_reqs = g.get("requirement_ids") or g.get("requirements") or g.get("child_requirement_ids") or []
        child_names = [r.get("name", r.get("id", "")) if isinstance(r, dict) else str(r) for r in child_reqs]
        n_count = g.get("min_count") or g.get("target_count") or 1

        satisfied_count = 0
        unknown_count = 0
        failed_count = 0
        child_explanations: list[str] = []

        for name in child_names:
            r = res_map.get(name.lower())
            if r:
                if r.is_satisfied:
                    satisfied_count += 1
                    child_explanations.append(f"{name}: satisfied")
                elif r.match_category == RequirementMatchCategory.UNKNOWN:
                    unknown_count += 1
                    child_explanations.append(f"{name}: unknown")
                else:
                    failed_count += 1
                    child_explanations.append(f"{name}: not evidenced")
            else:
                unknown_count += 1
                child_explanations.append(f"{name}: unknown")

        # Evaluate by operator
        is_sat = False
        is_unk = False
        explanation = ""

        if op == "AND":
            # Required Test 132: AND logic requires all children satisfied
            if satisfied_count == len(child_names) and len(child_names) > 0:
                is_sat = True
                explanation = f"All {len(child_names)} requirements in AND group satisfied: {', '.join(child_explanations)}."
            elif failed_count > 0:
                is_sat = False
                explanation = f"AND group failed: {failed_count} condition(s) unmet: {', '.join(child_explanations)}."
            else:
                is_unk = True
                explanation = f"AND group uncertain: contains unknown conditions: {', '.join(child_explanations)}."

        elif op in ("OR", "EQUIVALENTALTERNATIVE"):
            # Required Test 133: OR logic satisfied if at least one alternative is satisfied
            if satisfied_count >= 1:
                is_sat = True
                explanation = f"OR group satisfied via accepted alternative ({satisfied_count} met): {', '.join(child_explanations)}."
            elif failed_count == len(child_names):
                is_sat = False
                explanation = f"OR group failed: none of the {len(child_names)} alternatives are met."
            else:
                is_unk = True
                explanation = f"OR group uncertain: pending unknown alternatives: {', '.join(child_explanations)}."

        elif op == "ATLEASTN":
            # AtLeastN logic
            target = n_count or 2
            if satisfied_count >= target:
                is_sat = True
                explanation = f"AtLeastN requirement satisfied: {satisfied_count} of {target} distinct skills met."
            elif (satisfied_count + unknown_count) < target:
                is_sat = False
                explanation = f"AtLeastN requirement unmet: only {satisfied_count} met, {target} required."
            else:
                is_unk = True
                explanation = f"AtLeastN requirement uncertain: {satisfied_count} met, {unknown_count} unknown, {target} required."

        else:
            is_sat = satisfied_count > 0
            explanation = f"Logical group evaluated: {satisfied_count} satisfied."

        group_res = GroupEvaluationResult(
            group_id=g_id,
            operator=op,
            target_count=n_count or 1,
            satisfied_count=satisfied_count,
            is_satisfied=is_sat,
            is_unknown=is_unk,
            explanation=explanation,
        )
        results.append(group_res)

    return results
