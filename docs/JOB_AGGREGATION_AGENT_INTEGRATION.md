# Recruitment Agent Integration & Capabilities (Stage 27)

## Overview
Stage 27 exposes 13 recruitment aggregation capabilities registered under the `job.aggregate.*` namespace, allowing AUTONOM multi-agent systems to query, resolve, merge, and reconcile job opportunities autonomously.

## Registered Agent Capabilities

| Capability ID | Description |
| :--- | :--- |
| `job.aggregate.get_overview` | Retrieve canonical aggregation metrics and telemetry. |
| `job.aggregate.list_jobs` | Query canonical jobs with filters (title, employer, location, mode). |
| `job.aggregate.get_job` | Retrieve full canonical job record with linked sources and locations. |
| `job.aggregate.get_job_sources` | Inspect source observations linked to a canonical job. |
| `job.aggregate.get_job_history` | Retrieve immutable version snapshots for a canonical job. |
| `job.aggregate.process_observation` | Ingest single source observation into canonical database. |
| `job.aggregate.sync_from_discovery` | Synchronize pending Stage 26 observations into canonical records. |
| `job.aggregate.list_duplicates` | Retrieve pending duplicate candidate review queue. |
| `job.aggregate.submit_duplicate_decision` | Submit human or agent resolution for duplicate candidate pair. |
| `job.aggregate.merge_jobs` | Transactionally merge duplicate canonical job identities. |
| `job.aggregate.split_job` | Transactionally split detached sources into a new canonical job. |
| `job.aggregate.resolve_employer` | Run on-demand 5-stage employer identity resolution. |
| `job.aggregate.resolve_conflict` | Resolve field-level discrepancy on canonical job. |

## Inter-Stage Agent Workflows
- **Stage 26 $\to$ Stage 27**: As discovery connectors harvest new postings, they emit observations that are incrementally consumed by Stage 27's batch aggregation processor.
- **Stage 27 $\to$ Stage 28**: Downstream Job Requirement Intelligence consumes canonical jobs and authoritative description references rather than noisy, un-deduplicated raw postings.
