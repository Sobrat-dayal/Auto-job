# Lever Published Postings Connector (Stage 26)

## Overview
The Lever connector communicates with the official Lever Postings API.

- **Official API Documentation**: `https://github.com/lever/postings-api`
- **Base Endpoint**: `https://api.lever.co/v0/postings/{site}?mode=json`
- **Detail Endpoint**: `https://api.lever.co/v0/postings/{site}/{posting_id}`
- **Authentication**: None required for published public listings.
- **Pagination**: Supports bounded query parameters: `limit` (max 100) and `skip`.

## Configuration
```json
{
  "name": "Netflix Careers",
  "connector_id": "lever",
  "official_domain": "api.lever.co",
  "site_id": "netflix",
  "employer_name": "Netflix",
  "rate_limit_rpm": 30
}
```

## Extracted Fields & Normalization
- `native_posting_id`: Lever posting UUID (`posting.id`).
- `title`: `posting.text`.
- `official_posting_url`: `posting.hostedUrl`.
- `application_url`: `posting.applyUrl`.
- `location`: Parsed from `posting.categories.location` and `posting.workplaceType` (remote, hybrid, onsite).
- `department`: Extracted from `posting.categories.team` or `posting.categories.department`.
- `employment_type`: Mapped from `posting.categories.commitment` (`Full-Time` -> `full_time`, etc.).
- `compensation`: Extracted from description plain text or salary ranges.
