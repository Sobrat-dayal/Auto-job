# Job Source Observation Model and Provenance (Stage 26)

## Provider-Neutral Observation Architecture
A `JobSourceObservation` represents a factual, timestamped observation of a vacancy published by an external source. It avoids premature deduplication or destructive merges, leaving entity resolution to Stage 27.

```typescript
export interface JobSourceObservation {
  id: string;                         // obs_xxx
  source_id: string;                  // Configured source ID
  provider: ConnectorId;              // greenhouse, lever, ashby, usajobs, etc.
  native_posting_id: string;          // Provider's unique posting identifier
  source_url: string;                 // Official listing URL
  title: string;                      // Cleaned job title
  employer: string;                   // Resolved employer string
  location: ExtractedLocation;        // City, country, workplace type (remote/hybrid)
  employment_type?: string | null;    // full_time, part_time, internship, contract
  compensation?: ExtractedCompensation | null; // Published salary range (never guessed)
  description_text: string;           // Sanitized plain text
  application_url?: string | null;    // Direct application URL
  department?: string | null;         // Team or department
  posted_at?: string | null;          // ISO 8601 published date
  updated_at?: string | null;         // ISO 8601 updated date
  discovered_at: string;              // First observed timestamp
  last_fetched_at: string;            // Most recent successful check
  availability: PostingAvailability;  // available, closed, expired, removed
  prefilter_status: PrefilterOutcome; // prefilter_accepted, prefilter_rejected, needs_review
  prefilter_reasons: string[];        // Policy justifications
  snapshot_id?: string | null;        // Snapshot identifier
  extraction_version: string;
}
```

## Field Provenance Tracking
Every extracted attribute records:
- `raw_field_path`: Dot notation path in provider's raw payload (e.g. `jobs.compensation.compensationTierSummary`).
- `parser_method`: Extraction mechanism (`json_ld`, `json_key`, `html_sanitizer`, `regex_range`).
- `confidence`: `HIGH`, `MEDIUM`, or `LOW`.
- `retrieved_at`: UTC timestamp of extraction.
