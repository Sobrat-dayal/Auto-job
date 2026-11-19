# USAJOBS Connector (Stage 26)

## Overview
The USAJOBS connector integrates with the official US Federal Government USAJOBS Search API.

- **Official API Documentation**: `https://developer.usajobs.gov/API-Reference/Get-Job-Information`
- **Base Endpoint**: `https://data.usajobs.gov/api/search`
- **Authentication**: Requires two mandatory HTTP request headers:
  - `User-Agent`: Contact email address registered with USAJOBS Developer Portal.
  - `Authorization-Key`: Registered Developer API Key.

## Gated Capability & Mock Fallback
When API credentials are not provided:
1. `validate_source` returns `access_status: "requires_credentials"`.
2. The source remains disabled until the user supplies their registered API key.
3. Unit tests use fixture mocks without calling external federal servers.

## Extracted Fields & Federal Specifics
- `native_posting_id`: Position ID / MatchedObjectId.
- `title`: `MatchedObjectDescriptor.PositionTitle`.
- `employer_name`: Federal Department / Agency (e.g. `Department of Defense`, `NASA`).
- `location`: Parsed from `PositionLocationDisplay`.
- `compensation`: Extracted from `PositionRemuneration` (minimum and maximum base salary).
- `closing_date`: Extracted from `ApplicationCloseDate`.
