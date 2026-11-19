# Continuous Recruitment Monitoring Architecture (Stage 30)

## 1. System Overview
The AUTONOM Continuous Recruitment Monitoring Engine (Stage 30) represents the fifth and final stage of **Phase 6 — Autonomous Job Discovery & Matching**. It transforms the discrete intelligence and matching engines (Stages 25–29) into an ongoing, persistent, schedule-driven autonomous monitoring, change detection, and opportunity prioritization pipeline.

```
+---------------------------------------------------------------------------------------------------+
|                                 AUTONOM RECRUITMENT MONITORING PIPELINE                           |
+---------------------------------------------------------------------------------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |      Intelligent Recurrence Scheduler            |
                         |   (Timezone-aware, Interval >=5m, Quiet Hours)   |
                         +------------------------+-------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |       Worker Lease & Rate Limit Controller       |
                         |  (SQLite atomic locks, Heartbeats, Cooldowns)    |
                         +------------------------+-------------------------+
                                                  |
    +---------------------------------------------+---------------------------------------------+
    |                                             |                                             |
    v                                             v                                             v
+-----------------------+             +-----------------------+             +-----------------------+
|  Job Board APIs       |             | Employer Career Pages |             | Direct Feed Ingestion |
|  (Greenhouse, Lever)  |             | (Authorized portals)  |             | (RSS / JSON / USAJOBS)|
+-----------+-----------+             +-----------+-----------+             +-----------+-----------+
            |                                     |                                     |
            +-------------------------------------+-------------------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |       Canonical Job Reconciliation Engine        |
                         |        (Entity deduplication & updates)          |
                         +------------------------+-------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |       Semantic Job Change Detection              |
                         |  (Normalizes whitespace/HTML, detects salary,    |
                         |   location, remote conditions, and closures)     |
                         +------------------------+-------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |      Dependency Graph & Evaluation Refresh       |
                         |   (Selectively updates requirements & matching)  |
                         +------------------------+-------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |      Prioritized Opportunity Queue & Handoff     |
                         |    (Produces OpportunityPreparationCandidate    |
                         |      for Stage 31 Application Preparation)       |
                         +------------------------+-------------------------+
                                                  |
                         +------------------------v-------------------------+
                         |        Alert Engine & Notification Outbox        |
                         |   (Deduplicated toasts, in-app feed, quiet hours)|
                         +--------------------------------------------------+
```

## 2. Core Architectural Pillars
1. **Durable Watch Configurations (`RecruitmentJobWatchModel`)**:
   Watches define recurring observation targets, approved platform sources, employer IDs, role/location filters, and timezone-aware schedule parameters.
2. **Deterministic Recurrence & Quiet Hours**:
   Supports fixed intervals (enforced $\ge 5$ minutes), daily, weekdays-only, and weekly schedules. Quiet hours dynamically evaluate cross-midnight intervals to suppress notifications or pause network activity.
3. **Atomic Worker Leases & Distributed Safety**:
   Backed by SQLite with expiring leases (`expires_at`), heartbeat renewal, and automated cleanup on system startup or wake.
4. **Selective Invalidation & Dependency Graph**:
   When job listings change, the engine identifies material changes (salary range, location, remote conditions, status) vs superficial formatting modifications, triggering selective downstream requirement and match recalculation without unnecessary AI consumption.
5. **Stage 31 Readiness Handoff**:
   Eligible, highly ranked opportunities passing all hard career policies generate immutable `OpportunityPreparationCandidate` contracts ready for application tailoring.
6. **Safety & Zero Autonomous Submissions**:
   Stage 30 strictly enforces read-only discovery, ranking, and queueing. Zero applications are submitted, zero recruiters are messaged, and emergency stop / automation pause states are respected instantaneously.
