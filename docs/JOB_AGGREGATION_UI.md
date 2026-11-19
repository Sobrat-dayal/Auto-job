# Job Aggregation Desktop User Interface (Stage 27)

## Overview
The **Job Aggregation Workspace** (`JobAggregationWorkspace.tsx`) provides an operations dashboard for inspecting canonical vacancies, reviewing potential duplicates, resolving employer identities, and managing field discrepancies.

## UI Navigation & Layout
- **URL Route**: `/recruitment/aggregation`
- **Navigation Group**: `RECRUITMENT` $\to$ `Jobs & Applications` $\to$ `Job Aggregation & Canonical Database` (Roadmap Stage: Stage 27).

## Workspace Tabs

### 1. Overview & Telemetry
- Key KPI cards: Total Source Observations, Total Canonical Jobs, Multi-Source Canonical Jobs, Pending Duplicate Reviews, Confirmed Duplicate Merges, Active Field Conflicts.
- Engine Health Card with database connection status, resolved employer count, and auto-merge threshold indicators.
- One-click "Sync from Discovery" action.

### 2. Canonical Jobs Directory
- Real-time search filter across job title, requisition ID, and location.
- Status dropdown (All, Active, Possibly Active, Closed).
- Interactive card view with status badges, version number, employer name, requisition code, and source count badge.
- "Inspect Details" button navigating directly to Job Details view.

### 3. Job Details & Provenance Inspector
- Deep inspection drawer presenting primary listing URL, requisition number, and compensation.
- Provenance list showing all linked Stage 26 source observations with native posting IDs and source URLs.
- Version history timeline displaying audit revisions and change summaries.

### 4. Canonical Employers Directory
- Directory of verified employers with organization types (`Direct Employer`, `Staffing Agency`).
- Interactive **On-Demand Employer Identity Resolver**: allows manual testing of employer name and URL to preview 5-stage identity resolution.

### 5. Duplicate Review Queue
- Side-by-side comparison of duplicate candidate pairs (Job A vs Job B).
- Similarity score badge and matching factors.
- Action buttons: "Confirm & Merge", "Keep Separate", and "Mark Related".

### 6. Merge & Split Operations Center
- Interactive transactional merge interface: input surviving job ID and superseded job ID, preview merge impact, and execute merge.
- Interactive transactional split interface: input canonical job ID, select checkboxes for sources to detach, and execute atomic split.

### 7. Field Conflicts Resolver
- Displays conflicting values across sources for salary, remote status, or employment type.
- One-click resolution choosing authoritative source value or custom override.

### 8. Aggregation Tasks History
- Audit table of background batch tasks, processed counts, and completion statuses.

### 9. Aggregation Policy & Settings
- Auto-merge toggle and similarity threshold slider ($0.80 - 0.99$).
- Strict requisition matching enforcement toggle.
