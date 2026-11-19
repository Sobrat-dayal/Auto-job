# Job Ranking Explainability & Counterfactual Scenarios

## 1. Transparent Mathematical Breakdown
Every evaluated vacancy exposes its full mathematical breakdown in `score_breakdown`:
- Exact raw score for each dimension ($0.0 \text{ to } 1.0$).
- Configured weight and resulting weighted score.
- Human-readable narrative explanation for why points were earned or deducted.
- Total observed weight and list of missing/unobserved dimensions.

## 2. Counterfactual Explanations
When an applicant is deemed ineligible or lower priority, the engine generates actionable counterfactual statements:
- Example: *"Acquiring verified competency in SQL would eliminate the blocking mandatory gap and elevate this opportunity from Ineligible to Eligible & Aligned (Simulated Relevance: 88.5/100)."*
- Example: *"Confirming work authorization for the United Kingdom would resolve the pending human review request."*
- Enables applicants to see exactly what factual adjustments would transform ineligibility into actionable opportunities.
