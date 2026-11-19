# Opportunity Ranking Engine & Rubric Architecture

## 1. 8 Transparent Rubric Dimensions
The relevance index ($0.0 \text{ to } 100.0$) is calculated as a normalized weighted sum across 8 dimensions:

```
Relevance Index = (Sum of Observed Weighted Scores / Sum of Observed Dimension Weights) * 100
```

| Dimension | Default Weight | Description |
| :--- | :--- | :--- |
| `qualification_alignment` | 0.25 | Mandatory prerequisite coverage ratio |
| `preferred_skills` | 0.15 | Desirable bonus skill coverage ratio |
| `role_family` | 0.15 | Alignment with active career strategy target roles |
| `experience_duration` | 0.10 | Professional tenure comparison against mandated minimum |
| `work_arrangement` | 0.10 | Remote / Hybrid / Onsite compatibility with user preferences |
| `compensation` | 0.10 | Annualized salary overlap factor with user expectations |
| `employer_preference` | 0.05 | Preferred employer bonus points |
| `posting_freshness` | 0.10 | Decay factor based on discovery timestamp (0 to 60 days) |

## 2. Deterministic Prioritization Queue & Tie-Breaking
Candidate vacancies are prioritized into queue tiers:
1. `EligibleAndAligned` (Tier 1)
2. `ConditionallyEligible` (Tier 2)
3. `EligibleButLowerPriority` (Tier 3)
4. `RequiresApplicantReview` (Tier 4)
5. `MissingCriticalInformation` (Tier 5)
6. `KnownRequirementNotMet` (Tier 6)
7. `RejectedByHardPolicy` (Tier 7)

**Tie-Breaking Key**:
`(Tier Priority, -Relevance Index, -Mandatory Ratio, -Preferred Ratio, Canonical Job ID)`
Ensures stable, deterministic ordering across runs and client restarts.
