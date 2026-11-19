# Ashby Public Job Postings Connector (Stage 26)

## Overview
The Ashby connector retrieves published opportunities from Ashby's public board posting API.

- **Base Endpoint**: `https://api.ashbyhq.com/posting-api/job-board/{board_token}`
- **Authentication**: None required for published public boards.
- **Payload Schema**: Structured JSON response containing a `jobs` array with explicit compensation tier summaries and department metadata.

## Configuration
```json
{
  "name": "OpenAI Careers",
  "connector_id": "ashby",
  "official_domain": "api.ashbyhq.com",
  "board_token": "openai",
  "employer_name": "OpenAI",
  "rate_limit_rpm": 30
}
```

## Extracted Fields & Normalization
- `native_posting_id`: Ashby job UUID (`job.id`).
- `title`: `job.title`.
- `official_posting_url`: `job.jobUrl`.
- `application_url`: `job.applyUrl`.
- `location`: Parsed from `job.location` string and `job.isRemote` flag.
- `department`: Extracted from `job.department` or `job.team`.
- `compensation`: Extracted directly from `job.compensation.compensationTierSummary` (e.g. `"$245,000—$320,000 USD"`). Both en-dash (`–`) and em-dash (`—`) ranges are parsed cleanly.
