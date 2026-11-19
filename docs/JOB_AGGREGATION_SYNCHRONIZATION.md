# Job Aggregation Synchronization & Batch Checkpointing (Stage 27)

## Overview
The aggregation engine synchronizes observations from Stage 26 through an idempotent, batch-oriented pipeline equipped with checkpointing and error isolation.

## Synchronization Pipeline
```mermaid
flowchart TD
    DISC["Stage 26 Discovery Observations"] --> FETCH["Batch Observation Fetch"]
    FETCH --> CHECK["Idempotency Gate"]
    CHECK -->|Already Ingested| SKIP["Skip Ingestion"]
    CHECK -->|New Observation| PROC["Process Observation Pipeline"]
    PROC --> DECIDE{"Duplicate Score"}
    DECIDE -->|≥ 0.92| MERGE["Auto-Merge into Surviving Job"]
    DECIDE -->|0.75 - 0.91| QUEUE["Queue to Review"]
    DECIDE -->|< 0.75| CREATE["Create New Canonical Job"]
    MERGE --> CP["Update Aggregation Checkpoint"]
    QUEUE --> CP
    CREATE --> CP
    CP --> TASK_FIN["Complete Aggregation Task"]
```

## Fault Tolerance & Checkpoint Architecture
- **Task Model (`aggregation_tasks`)**: Tracks execution status (`pending`, `running`, `completed`, `failed`), total observations, processed counts, and performance metrics.
- **Checkpoint Model (`aggregation_checkpoints`)**: Persists `last_processed_observation_id` and processing counts, allowing large batch aggregation tasks to safely resume after process restarts or network interruptions.
- **Error Model (`aggregation_errors`)**: Isolates individual observation errors without failing entire aggregation batches.
