# Job Monitoring Dependency Invalidation (Stage 30)

## 1. Selective Downstream Invalidation
Rather than executing brute-force re-evaluations across all stored vacancies, the monitoring engine uses a dependency graph to invalidate only affected artifacts:

```
[Job Update Event]
        |
        +---> [Material Description Change?]
        |            |-- YES --> Invalidate Stage 28 Requirements Record
        |            |-- NO  --> Skip Requirement Analysis
        |
        +---> [Requirements or Attributes Changed?]
                     |-- YES --> Invalidate Stage 29 Matching Evaluation
                     |-- NO  --> Keep Existing Match Cache
```

## 2. Invalidation Events Handled
- **`job_closed`**: Sets listing availability to `closed`, propagates to `recruitment_opportunity_queue.job_availability`, marks readiness `False`, and preserves historical match audit records.
- **`description_updated`**: Invalidates cached intelligence record (`is_current = False`), queues vacancy for Stage 28 requirement extraction, and queues Stage 29 match re-evaluation.
- **`salary_or_location_changed`**: Directly updates Stage 29 compatibility details without re-running NLP requirement extraction.
- **`profile_updated`**: When applicant skills or claims update (Stage 21/22), invalidates evaluations for active queue entries.
- **`policy_updated`**: When career preferences update (Stage 25), re-evaluates policy eligibility and resets opportunity priorities.
