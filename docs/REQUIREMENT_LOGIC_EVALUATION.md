# Requirement Logic Evaluation

## 1. 3-Valued Logic System
The engine uses true, false, and unknown (`RequirementMatchCategory.UNKNOWN`) across nested requirement groups.

| Operator | Rule | Condition for Pass (`is_satisfied=True`) | Condition for Fail | Condition for Unknown |
| :--- | :--- | :--- | :--- | :--- |
| `AND` | All children must be satisfied | `satisfied_count == len(children)` | `failed_count > 0` | No failures, but `unknown_count > 0` |
| `OR` | At least one child must be satisfied | `satisfied_count >= 1` | `failed_count == len(children)` | No passes, but `unknown_count > 0` |
| `AtLeastN` | At least N children must be satisfied | `satisfied_count >= target_n` | `(satisfied + unknown) < target_n` | `satisfied < target_n` and `(satisfied + unknown) >= target_n` |

## 2. Acceptable Equivalent Alternatives
When an employer specifies equivalent alternatives (e.g. "Bachelor's degree in Computer Science OR 4+ years practical software development experience"):
- Handled via `OR` or `EquivalentAlternative` logic groups.
- Satisfying any single alternative satisfies the group.
- The unchosen alternative is NOT recorded as a blocking qualification gap.
- Atomic requirements inside satisfied alternative groups do not trigger `KnownRequirementNotMet`.
