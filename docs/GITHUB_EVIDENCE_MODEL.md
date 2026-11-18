# Stage 22: GitHub Technical Evidence Model

## 1. Evidence Artifact Structure

To support the Zero-Hallucination mandate of AUTONOM, every technical claim extracted from GitHub is encapsulated in a tamper-evident evidence model.

### 1.1 Data Schema
```typescript
interface GitHubEvidenceItem {
  id: string;                         // Unique evidence UUID
  repo_id: string;                    // Associated repository ID
  repo_full_name: string;             // owner/repo
  evidence_type: "manifest_dependency" | "source_code" | "commit_history" | "pull_request";
  file_path?: string;                 // Path relative to repository root
  commit_sha?: string;                // 40-character Git commit hash
  line_numbers?: string;              // e.g. "L12-L28"
  source_excerpt?: string;            // Exact text/code snippet
  secret_redacted: boolean;           // True if sanitized by SecretRedactor
  attribution_level: AttributionLevel;
  discovered_at: string;              // ISO-8601 timestamp
}
```

---

## 2. Cryptographic & Temporal Anchoring

1. **Commit SHA Anchoring**: Source files, architecture findings, and contributions are tied directly to the immutable 40-character SHA of the default branch commit or specific contribution commit. Even if a remote branch is later rebased or deleted, the evidence points to the exact historical snapshot inspected.
2. **Path Normalization**: File paths are normalized to Unix style (`src/services/auth.ts`) and verified by `SourceFilter.is_safe_relative_path()` to ensure no directory traversal (`../`) attacks compromise the evidence registry.
3. **Redaction Auditing**: If `SecretRedactor` modifies the excerpt (e.g., masking an accidental embedded token or connection string), `secret_redacted=True` is recorded, and the clean, masked excerpt is preserved. Raw secrets are never saved in the evidence payload.
