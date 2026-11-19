# Job Aggregation Security & Access Governance (Stage 27)

## Overview
The canonical aggregation engine strictly enforces data privacy, local execution boundaries, and role-based permissions in accordance with AUTONOM's security model.

## Security Architecture

### Local Execution & Air-Gapped Operation
All entity resolution, similarity scoring, database records, and version histories reside strictly on the user's local Windows workstation in an encrypted SQLite database. No candidate data, employer records, or vacancy details are exfiltrated to external analytics servers.

### Scoped Permissions (Stage 14 Integration)
Operations on canonical database records are protected by fine-grained permissions:
- `recruitment.jobs.canonical.read`: View canonical jobs and linked sources.
- `recruitment.jobs.canonical.create`: Ingest observations and create canonical entities.
- `recruitment.jobs.canonical.update`: Update canonical fields and reconcile conflicts.
- `recruitment.jobs.merge`: Authorize and execute canonical job merges.
- `recruitment.jobs.split`: Separate previously merged source links.
- `recruitment.jobs.duplicate_review`: Resolve duplicate review queue items.
- `recruitment.employers.read`: View employer directory and aliases.
- `recruitment.employers.resolve`: Trigger employer identity resolution.
- `recruitment.employers.correct`: Apply manual employer corrections and aliases.

### Career Policy Pre-Filter Integration (Stage 25)
Before an incoming job is promoted to active canonical status, its resolved employer name, domain, and staffing status are evaluated against the Stage 25 Employer Blocklist:
- Blocklisted companies are assigned `identity_status = 'rejected'` or filtered out from candidate matching queues.

### Safety Invariants
1. **Zero External API Scraping / CAPTCHA Bypassing**: Uses only authorized Stage 26 public APIs, career pages, and user imports.
2. **Zero Automated Job Applications**: Strictly reserved for Stage 31+ with explicit user consent.
3. **Zero Recruiter Outreach**: No cold messaging or automated recruiter communication.
