# What-If Scenario Simulator

## 1. Zero-Mutation Architecture (Required Test 154)
The What-If Simulation Engine allows applicants and recruitment agents to test hypothetical adjustments:
- What if I add Python or AWS to my confirmed skills?
- What if I lower my minimum salary expectation from $150k to $125k?
- What if I obtain verified work authorization for the United Kingdom?
- What if I complete my degree?

### Data Isolation Guarantee
- The simulator operates strictly on deep copies (`copy.deepcopy`) of inputs.
- Zero database mutations occur.
- Profile claims, active career policies, and baseline evaluation records remain completely untouched.

## 2. Simulation Response
- `original_relevance_index` vs `simulated_relevance_index`.
- `original_eligibility` vs `simulated_eligibility`.
- `diff_explanation`: Clear narrative describing score changes and gap resolutions.
- `dimension_diffs`: Exact point differences per rubric dimension.
- `remaining_gaps`: Unresolved qualification gaps that still persist.
