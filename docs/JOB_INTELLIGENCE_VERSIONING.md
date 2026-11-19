# Analysis Versioning & Reanalysis Triggers (Stage 28)

## 1. Overview
Employers frequently update job descriptions during active recruiting cycles. The Job Intelligence Engine tracks description versions using SHA-256 content hashing to trigger incremental reanalysis and archive historical intelligence records.

## 2. Content Hashing
```python
def compute_description_hash(cleaned_description_text: str) -> str:
    return hashlib.sha256(cleaned_description_text.strip().encode("utf-8")).hexdigest()
```

## 3. Reanalysis Triggers
1. **Source Content Change**: When a new fetch from Stage 26 yields a description with a different `description_hash`.
2. **Extractor Upgrade**: When `extractor_version` changes (e.g. from `1.0.0` to `1.1.0`), marking existing analyses as `Outdated`.
3. **Explicit User Force**: When a user or specialist agent calls `POST /api/v1/job-intelligence/jobs/{id}/analyze` with `force=True`.

## 4. Version Snapshotting
When reanalysis occurs on an existing intelligence record:
1. The previous intelligence snapshot is archived into `job_intelligence_versions` with an incremented `version_number` and change summary.
2. The existing `job_intelligence_records` row is updated in place.
3. Outdated atomic requirements are replaced, while historical review resolutions are audited.
