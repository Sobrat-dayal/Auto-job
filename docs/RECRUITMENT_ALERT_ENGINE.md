# Recruitment Alert Rules & Event Engine (Stage 30)

## 1. Alert Architecture
The Alert Engine continuously evaluates incoming job discovery events and match updates against user-defined notification rules.

```
[Job Event / Match Update]
            |
            v
[Alert Rule Evaluator]
            |
            v
[Fingerprint & Cooldown Tracker] ---- (Suppressed if duplicate within window)
            |
            v
[RecruitmentAlertEvent Persistence]
            |
            v
[Durable Notification Outbox]
     |                 |
     v                 v
[In-App Toast]    [Windows Desktop Toast]
```

## 2. Trigger Types Supported
- **`new_job`**: Newly discovered vacancy matching watch search criteria.
- **`high_priority_job`**: Opportunity whose relevance index exceeds configured score threshold (e.g. $\ge 85\%$).
- **`approaching_deadline`**: Application deadline expiring within configured window (e.g. $\le 48$ hours).
- **`material_job_change`**: Material updates to compensation, location, or remote arrangements.
- **`job_closed` / `job_reopened`**: Vacancy status transitions.
- **`review_required`**: New human review flag raised.
- **`source_failure`**: Upstream connector errors or rate-limit warnings.

## 3. Cooldown & Deduplication
To prevent alert storms, alerts calculate a SHA-256 fingerprint:
$$\text{fingerprint} = \text{SHA256}(\text{owner\_id} : \text{trigger\_type} : \text{canonical\_job\_id} : \text{source\_id})$$
Repeated occurrences within the rule's cooldown window (default: 30–60 minutes) are automatically suppressed.
