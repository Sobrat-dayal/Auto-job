# Job Field Reconciliation & Conflict Management (Stage 27)

## Overview
When multiple job boards list the same vacancy with differing descriptions, salary figures, or workplace policies, Stage 27 reconciles these discrepancies using a deterministic **Source Authority Hierarchy** and explicit conflict records.

## Source Authority Ranking
The authority score determines preferred field selection when multiple values are presented:

| Source Provider | Authority Score | Rationale |
| :--- | :--- | :--- |
| `career_page` / Direct Career Portal | `0.95` | Direct employer control, authoritative source of truth |
| `greenhouse` / Official ATS Board | `0.88` | Direct ATS public API integration |
| `lever` / Official ATS Board | `0.88` | Direct ATS public API integration |
| `ashby` / Official ATS Board | `0.88` | Direct ATS public API integration |
| `usajobs` / Government API | `0.92` | Official federal hiring portal |
| `manual_import` / User Supplied | `0.85` | User verified posting import |
| `url_import` / Direct URL | `0.80` | Directly crawled employer page |
| `structured_json` / Partner Feeds | `0.70` | Secondary structured ingestion |
| `rss_atom` / Public Feed | `0.65` | Syndicated feed; potential lag |
| `third_party_aggregator` | `0.50` | Scraping aggregators; lowest reliability |

## Conflict Resolution Lifecycle
1. **Conflict Detection**:
   - Compares incoming fields against established canonical fields.
   - If salary ranges, workplace arrangements, or employment types conflict, a record is created in `canonical_job_conflicts`.
2. **Conservative Default**:
   - The field value from the highest authority source is selected for display.
3. **Manual Resolution**:
   - Users or authorized agents can resolve conflicts via `/api/v1/job-aggregation/conflicts/{id}/resolve`.
   - Resolution records `chosen_value`, `resolved_by`, and audit timestamp.
