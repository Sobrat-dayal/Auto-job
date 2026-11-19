# Education Matching & Practical Equivalency

## 1. Degree Hierarchy & Status Compatibility
Educational degrees are mapped into a standardized hierarchical ladder:
- `Doctorate` (Level 5)
- `Master` (Level 4)
- `Bachelor` (Level 3)
- `Associate` (Level 2)
- `High School` (Level 1)
- `None` (Level 0)

### Graduation Status Distinction (Required Test 135)
- `academic_status == "currently_enrolled"` is strictly separated from `"completed"`.
- Enrolled students with anticipated graduation in future years do NOT satisfy requirements mandating completed degrees upon hiring.
- Evaluated as `KNOWN_NOT_SATISFIED`, generating a critical review or blocking gap.

## 2. Practical Experience Equivalency Waivers (Required Test 134)
When job intelligence indicates an employer allows experience equivalency (e.g., "Bachelor's degree or 4+ years of relevant practical experience"):
- Candidate holding Associate degree with 5+ years of verified professional tenure receives `SATISFIED_BY_ALTERNATIVE`.
- The evaluation outcome is `CONDITIONALLY_ELIGIBLE`, preventing disqualification.
