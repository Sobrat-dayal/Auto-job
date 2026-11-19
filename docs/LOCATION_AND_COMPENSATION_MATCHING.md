# Location & Compensation Policy Matching

## 1. Remote Jurisdictions & Geographic Restrictions (Required Test 141)
- When a job is marked "Remote", the engine inspects allowed jurisdiction countries (`allowed_countries`).
- If an employer advertises "Remote (US Only)" and applicant is resident in India with no US work authorization:
  - Hard constraint is violated (`hard_policy_passed=False`).
  - Evaluation produces `REJECTED_BY_HARD_POLICY`.
- Location blocklists from Career Strategy (`excluded_locations`) trigger immediate rejection.

## 2. Compensation Matching (Required Test 142)
### Pay Period Annualization
- All compensation rates are converted to an annualized baseline using standard working constants:
  - Hourly: $\text{amount} \times 2,080$ hours/year.
  - Monthly: $\text{amount} \times 12$ months/year.
  - Weekly: $\text{amount} \times 52$ weeks/year.

### Compatibility Outcomes
1. **Range Exceeds Minimum**: Job minimum meets or exceeds applicant minimum floor $\rightarrow$ Satisfied, high score factor.
2. **Partial Overlap**: Job maximum is above minimum floor, but job minimum is below $\rightarrow$ Compatible, score factor proportional to overlap fraction.
3. **Strictly Below Floor**: Job maximum is strictly below applicant minimum floor $\rightarrow$ Hard policy violation, `REJECTED_BY_HARD_POLICY`.
4. **Undisclosed Compensation**: Follows Career Strategy policy (`include`, `review`, or `exclude`).
