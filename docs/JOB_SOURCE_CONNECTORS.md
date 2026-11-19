# Job Source Connectors and Registry (Stage 26)

## Registered Connectors
AUTONOM implements an extensible connector plugin architecture managed by the central `ConnectorRegistry`. Every connector adheres to the `BaseSourceConnector` protocol:

| Connector ID | Provider Name | Category | Authentication | Default Rate Limit |
|---|---|---|---|---|
| `greenhouse` | Greenhouse Job Board API | `employer_ats_board` | None (Public Board) | 30 RPM |
| `lever` | Lever Postings API | `employer_ats_board` | None (Public API) | 30 RPM |
| `ashby` | Ashby Public Job Board API | `employer_ats_board` | None (Public Board) | 30 RPM |
| `usajobs` | USAJOBS Search API | `official_public_api` | Auth Key + User-Agent | 20 RPM |
| `rss_atom` | RSS / Atom Job Feed | `rss_atom_feed` | None (Public XML) | 30 RPM |
| `json_feed` | Structured JSON Feed | `structured_json_feed` | None / Custom Header | 30 RPM |
| `career_page` | Employer Career Portal | `employer_career_site` | None (Web / Schema.org) | 20 RPM |
| `manual_import`| Manual User Import | `manual_imported` | N/A (Local Entry) | N/A |
| `url_import` | Single URL Import | `user_supplied_url` | None (Direct Page Fetch) | N/A |

## Connector Manifest Schema
Each connector provides an immutable `ConnectorManifest` declaring its capabilities:

```typescript
export interface ConnectorManifest {
  connector_id: ConnectorId;
  version: string;
  provider_name: string;
  endpoint_category: SourceCategory;
  authentication_method: string;
  required_permissions: string[];
  supported_capabilities: ConnectorCapability[];
  provider_restrictions: string[];
  last_verified_doc_url: string;
  last_verified_at: string;
}
```

## Adding a Custom Connector
1. Subclass `BaseSourceConnector` in `services/api/app/recruitment/discovery/connectors/`.
2. Implement `validate_source`, `fetch_postings`, and `fetch_posting_detail`.
3. Register the connector instance in `ConnectorRegistry._register_default_connectors()`.
4. Export through `services/api/app/recruitment/discovery/connectors/__init__.py`.
