# Stage 22: GitHub Repository Discovery & Synchronization

## 1. Discovery Lifecycle

The `RepositoryDiscoveryService` discovers and catalogs code repositories associated with the connected account or manually ingested URLs.

```
       [User Actions]
             │
     ┌───────┴────────────────────────┐
     │                                │
     v                                v
Sync Repositories            Manual Repo Ingest
(GET /user/repos)         (https://github.com/o/r)
     │                                │
     └───────┬────────────────────────┘
             v
    [Metadata Normalization]
    - Repository ID (UUID)
    - Full Name (owner/repo)
    - Visibility (Public / Private)
    - Fork Lineage & Upstream URL
    - Stars, Forks, Watchers, Topics
    - Default Branch & Commit SHA
             v
    [Selection Management]
    - Selected for deep analysis (is_selected = True)
    - Deselected (is_selected = False)
             v
    [Source Tree Inspection]
    (GET /repos/{o}/{r}/git/trees/{sha}?recursive=1)
```

---

## 2. Manual Repository Ingestion

For applicants who maintain specialized work outside their primary account (e.g., enterprise open-source contributions or client work), AUTONOM provides direct URL ingestion via `/api/v1/github/repositories/manual`:
- Validates URLs conforming to `https://github.com/{owner}/{repo}` or `github.com/{owner}/{repo}`.
- Sanitizes repository slug and validates against GitHub API.
- Generates a localized repository record marked with `is_manual=True`.
- Respects the same safety filters, file limits, and secret redaction rules as discovered repositories.

---

## 3. Deep Source Tree Inspection (`SourceTreeInspector`)

Rather than performing dozens of discrete API calls to explore directories, AUTONOM leverages GitHub's Git Data Trees API:
`GET /repos/{owner}/{repo}/git/trees/{default_branch_sha}?recursive=1`

### 3.1 Efficiency & Safety Filters
In a single API call, AUTONOM retrieves a complete index of all files in the repository. The `SourceFilter` then applies strict heuristic rules:
1. **Size Bound**: Any blob exceeding 500 KB (`size > 512,000`) is flagged as `is_oversized` and skipped.
2. **Ignored Directories**: Files within `node_modules/`, `target/`, `dist/`, `build/`, `vendor/`, `.git/`, `.idea/`, `venv/`, and `.venv/` are excluded from content fetching.
3. **Binary & Asset Detection**: Images (`.png`, `.jpg`, `.svg`), binaries (`.exe`, `.dll`, `.so`, `.dylib`), fonts (`.woff`, `.ttf`), and audio/video files are cataloged as binary entries and not retrieved.
4. **Candidate Manifest Identification**: The inspector prioritizes manifest files (`package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`), CI workflows (`.github/workflows/*.yml`), Dockerfiles, and top-level entrypoints (`main.py`, `src/index.ts`, `app.py`).
5. **Execution Quota**: A maximum of 60 relevant files are retrieved per repository, capping network bandwidth and processing time.
