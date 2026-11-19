# Greenhouse Job Board Connector (Stage 26)

## Overview
The Greenhouse connector integrates directly with Greenhouse's official public Job Board API.

- **Official API Documentation**: `https://developers.greenhouse.io/job-board.html`
- **Base Endpoint**: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`
- **Detail Endpoint**: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{job_id}`
- **Authentication**: None required for published public boards.

## Configuration
```json
{
  "name": "Stripe Careers",
  "connector_id": "greenhouse",
  "official_domain": "boards-api.greenhouse.io",
  "board_token": "stripe",
  "employer_name": "Stripe",
  "rate_limit_rpm": 30
}
```

## Extracted Fields & Normalization
- `native_posting_id`: Integer job ID converted to string (e.g. `998877`).
- `title`: Clean role title.
- `official_posting_url`: `job.absolute_url` (e.g. `https://boards.greenhouse.io/stripe/jobs/998877`).
- `location`: Parsed from `job.location.name`. Remote status detected via keyword matching.
- `department`: Extracted from first entry in `job.departments[].name`.
- `office`: Extracted from first entry in `job.offices[].name`.
- `description_html` & `description_text`: Cleaned HTML and formatted plain text with bullet points.
- `compensation`: Extracted from description body using non-guessing regex parser.
