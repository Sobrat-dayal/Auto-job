# Job Discovery Policy Pre-filtering Integration (Stage 26)

## Overview
Discovered job postings are automatically pre-filtered against the user's active career preference strategy (established in Stage 25, `strat_backend_01`). This eliminates non-viable postings early in the pipeline before expensive deep matching or document tailoring occurs.

## Evaluation Rules
When an opportunity is observed, `DiscoveryCoordinator._evaluate_prefilter` executes the following checks:

1. **Blocked Employer Check**:
   If `posting.employer_name` matches an entry in `strategy.employers.blocked_employers`, the posting is immediately tagged `PREFILTER_REJECTED` with the blocked rationale.
2. **Excluded Role Titles Check**:
   If the job title contains an excluded target role title (e.g. `Senior Engineering Manager` in a technical IC strategy), it is tagged `PREFILTER_REJECTED`.
3. **Compensation Floor Check**:
   If compensation is explicitly published and `max_amount < strategy.compensation.min_acceptable_amount` with `is_hard_minimum = True`, it is tagged `PREFILTER_REJECTED`.
4. **Work Arrangement Check**:
   If `strategy.work_arrangement.is_hard_constraint = True` and the posting's workplace type (e.g. `onsite`) is not in `strategy.work_arrangement.allowed_arrangements`, it is tagged `PREFILTER_REJECTED`.
5. **Geographic / Country Constraint**:
   If `remote_within_country_only = True` and the country does not match allowed countries, it is tagged `NEEDS_REVIEW`.
6. **Pass / Accept**:
   If all hard checks pass, the posting is tagged `PREFILTER_ACCEPTED`.
