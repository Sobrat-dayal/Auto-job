# Multi-Source Job Aggregation & Canonical Database Architecture (Stage 27)

## Executive Overview
Stage 27 of the AUTONOM 50-stage roadmap establishes the **Canonical Job Aggregation Engine**, bridging disparate Stage 26 job board observations into a reliable, authoritative, source-backed canonical job repository.

Its mission is to reconcile multi-source postings, resolve employer identities across legal aliases and staffing agencies, detect duplicates with negative match prevention, manage field-level conflicts, and maintain immutable version snapshots and alias supersession chains.

```mermaid
flowchart TD
    subgraph Stage26["Stage 26 Discovery Observations"]
        GH["Greenhouse Listings"]
        LV["Lever Postings"]
        AB["Ashby Openings"]
        CP["Employer Career Pages"]
        FEEDS["RSS / Atom / JSON Feeds"]
    end

    subgraph Stage27Ingest["Ingestion & Idempotency Pipeline"]
        IDEMP["Idempotency Gate (obs_id check)"]
        NORM["Multi-Field Normalizer (URLs, Reqs, Titles, Locs)"]
    end

    subgraph Stage27Resolution["Employer & Entity Resolution"]
        ATS_TOKEN["ATS Board Token Extraction"]
        LEGAL_NORM["Legal Suffix Stripping & Aliasing"]
        CORP_DOM["Corporate Domain Verification"]
        ORG_CLASS["Direct Employer vs Staffing Agency"]
        CAN_EMP[("canonical_employers")]
    end

    subgraph Stage27Deduplication["Intelligent Duplicate Engine"]
        BLOCK["Multi-Key Blocking Filter"]
        EXACT["Deterministic Match Rules"]
        NEG["Negative Evidence Evaluator (Strict Contradictions)"]
        SIM["Multi-Factor Weighted Similarity (0.0 - 1.0)"]
        QUEUE["Human Duplicate Review Queue"]
    end

    subgraph Stage27Reconciliation["Reconciliation & Integrity"]
        AUTH["Source Authority Rank Matrix"]
        FIELD_CAND["Field Candidate Selection"]
        CONFLICTS[("canonical_job_conflicts")]
        STATUS_REC["Conservative Status (Partial Snapshot Safe)"]
        VERSIONS[("canonical_job_versions")]
        ALIASES[("canonical_job_aliases")]
    end

    subgraph Stage27Storage["Canonical Job Repository"]
        CAN_JOBS[("canonical_jobs")]
        CAN_LINKS[("canonical_job_source_links")]
    end

    Stage26 --> IDEMP
    IDEMP --> NORM
    NORM --> ATS_TOKEN
    ATS_TOKEN --> LEGAL_NORM
    LEGAL_NORM --> CORP_DOM
    CORP_DOM --> ORG_CLASS
    ORG_CLASS --> CAN_EMP
    CAN_EMP --> BLOCK
    BLOCK --> EXACT
    EXACT --> NEG
    NEG --> SIM
    SIM -->|≥ 0.92| AUTH
    SIM -->|0.75 - 0.91| QUEUE
    SIM -->|< 0.75| CAN_JOBS
    QUEUE -->|Human Merge| AUTH
    AUTH --> FIELD_CAND
    FIELD_CAND --> CONFLICTS
    AUTH --> STATUS_REC
    STATUS_REC --> CAN_JOBS
    CAN_JOBS --> VERSIONS
    CAN_JOBS --> CAN_LINKS
    AUTH --> ALIASES
```

## Core Architectural Invariants
1. **Zero Automated Application Submissions**: Strictly reserved for Stage 31+ with human authorization.
2. **Deterministic Precedence over Heuristics**: Requisition numbers and verified employer career pages outrank third-party aggregators.
3. **Negative Evidence Dominance**: Conflicting requisition IDs under the same employer or differing seniority/employment types strictly prohibit automatic merging.
4. **Partial Snapshot Non-Closure**: Missing items from incomplete or interrupted feeds remain `possibly_active` rather than `closed`.
5. **Atomic Version Auditing**: Every merge, split, or field override appends an immutable revision to `canonical_job_versions`.
