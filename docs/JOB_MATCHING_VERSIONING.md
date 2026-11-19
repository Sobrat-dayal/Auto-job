# Evaluation Versioning, Caching & Invalidation Lifecycle

## 1. Immutable Input Hashing
Cache keys are computed using SHA-256 over immutable input version coordinates:
```
raw_key = f"{profile_id}:v{profile_version}:{canonical_job_id}:v{job_version}:{strategy_id}:{rubric_id}:v{rubric_version}"
cache_key = sha256(raw_key).hexdigest()
```
- If neither the applicant profile, job intelligence, career strategy, nor rubric has changed, identical evaluation results are returned instantaneously without re-computation.

## 2. Invalidation Events
1. **Applicant Profile Updates (Required Test 148)**:
   - When an applicant adds a skill, updates employment history, or modifies education, all current match evaluations for that profile are marked `is_current = False`.
2. **Canonical Job Updates (Required Test 149)**:
   - When a job's requirements, compensation, or status change, prior evaluations for that job are invalidated.
3. **Career Policy Updates (Required Test 150)**:
   - When the user modifies role families, location preferences, salary floors, or employer blocklists, evaluations associated with that strategy are invalidated.
