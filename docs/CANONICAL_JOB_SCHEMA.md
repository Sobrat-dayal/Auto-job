# Canonical Job Schema & Entity Structure (Stage 27)

## Overview
The canonical job schema represents the single authoritative record of a job vacancy in AUTONOM. It synthesizes observations from multiple sources, tracks field-level provenance, records geographical office instances, and maintains namespaced requisition identifiers.

## Schema Specifications

### `canonical_jobs` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | Stable UUID format `cjob_<uuid>` |
| `employer_id` | `VARCHAR(36)` | `FOREIGN KEY` | Ref to `canonical_employers.id` |
| `display_title` | `VARCHAR(255)` | `NOT NULL` | Chosen user-facing title |
| `normalized_title` | `VARCHAR(255)` | `NOT NULL`, `INDEX` | Canonical title representation |
| `requisition_id` | `VARCHAR(100)` | `INDEX` | Extracted internal job/req code |
| `employment_type` | `VARCHAR(50)` | `NULLABLE` | `full_time`, `contract`, `internship` |
| `location_summary` | `VARCHAR(255)` | `NULLABLE` | Human-readable location rollup |
| `work_arrangement` | `VARCHAR(50)` | `NULLABLE` | `remote`, `hybrid`, `onsite` |
| `description_reference` | `TEXT` | `NULLABLE` | Clean text reference for matching |
| `compensation_summary` | `VARCHAR(100)` | `NULLABLE` | Synthesized salary or pay string |
| `status` | `VARCHAR(30)` | `DEFAULT 'active'` | `active`, `possibly_active`, `closed` |
| `first_observed_at` | `DATETIME` | `NOT NULL` | Earliest discovery timestamp |
| `last_observed_at` | `DATETIME` | `NOT NULL` | Most recent source sighting |
| `last_verified_active_at` | `DATETIME` | `NULLABLE` | Verified active confirmation |
| `version` | `INTEGER` | `DEFAULT 1` | Monotonically increasing revision counter |
| `source_count` | `INTEGER` | `DEFAULT 1` | Total linked active sources |
| `identity_status` | `VARCHAR(30)` | `DEFAULT 'canonical'` | `canonical`, `in_review`, `rejected` |
| `conflict_state` | `VARCHAR(30)` | `DEFAULT 'no_conflict'` | Conflict tracking state |
| `primary_source_id` | `VARCHAR(100)` | `NULLABLE` | Preferred source identifier |
| `primary_url` | `VARCHAR(1024)` | `NULLABLE` | Canonical primary listing URL |
| `is_evergreen` | `BOOLEAN` | `DEFAULT FALSE` | Continuous pipeline posting |
| `is_repost` | `BOOLEAN` | `DEFAULT FALSE` | Closed and subsequently reopened |
| `created_at` | `DATETIME` | `NOT NULL` | Database creation timestamp |
| `updated_at` | `DATETIME` | `NOT NULL` | Last update timestamp |

### `canonical_job_source_links` Table
Maintains source-to-canonical provenance:
- `canonical_job_id`: Parent canonical job entity.
- `source_observation_id`: Ref to Stage 26 `job_source_observations.id`.
- `provider`: Connector used (`greenhouse`, `lever`, `ashby`, etc.).
- `native_posting_id`: Provider's native requisition ID.
- `original_url`: Normalized source listing URL.
- `is_primary`: Flag denoting whether this is the authoritative primary listing.
- `decision_method`: Provenance rule (`exact_rule`, `auto_merge`, `human_review`).
