# Job Source Access Policies and Permissions (Stage 26)

## Source Access Status Taxonomy
Every configured source maintains a deterministic access policy state:

| Status Enum | Meaning | Permitted Autonomous Behavior |
|---|---|---|
| `available_public` | Public API or feed without credentials | Full autonomous discovery & polling |
| `available_authorized` | Authenticated partner API with verified credentials | Autonomous discovery within quota |
| `requires_credentials` | Missing API key, bearer token, or email header | Paused until user inputs credentials |
| `requires_partner_access`| Provider requires enterprise partner agreement | Blocked; manual import alternative offered |
| `manual_import_only` | Unofficial/unsupported source | Manual URL import or text entry only |
| `temporarily_rate_limited`| HTTP 429 response received | Backoff active; discovery paused until Retry-After expires |
| `access_denied` | HTTP 401 or 403 authorization failure | Blocked; notifies user in UI |
| `restricted_by_terms` | Commercial platform whose terms prohibit automated retrieval | Automated fetching strictly forbidden |
| `unavailable` | 3+ consecutive network timeouts or 5xx server errors | Temporarily disabled by circuit breaker |
| `unverified` | Newly added source prior to initial connectivity check | Awaiting validation |

## Explicit Platform Restrictions
AUTONOM enforces an absolute ban on:
- Stealth scraping or spoofing browser headers to defeat commercial paywalls.
- CAPTCHA solving, bot bypass mechanisms, or residential proxy rotation.
- Automated bulk crawling of platforms whose Terms of Service strictly forbid scraping (e.g. LinkedIn, Indeed without partner API access).
- Ingesting third-party job aggregator dumps without verified employer provenance.
