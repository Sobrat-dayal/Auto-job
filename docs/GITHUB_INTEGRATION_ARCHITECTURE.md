# Stage 22: GitHub Integration Architecture

## 1. Overview & System Mission

The **GitHub Integration and Technical Portfolio Intelligence Engine** is the technical provenance backbone of AUTONOM's Recruitment Intelligence Foundation (Phase 5). Its mission is to transform raw, external code repositories into verified, evidence-backed professional qualifications without human exaggeration or LLM hallucination.

By interfacing directly with GitHub's REST and Git Data APIs, the engine discovers repositories, inspects manifest files and directory structures, identifies technology stacks, evaluates commit and pull request contributions, and generates candidate skills and projects. Crucially, these candidate claims are held in an isolated human-in-the-loop review queue before any data is synchronized into the canonical `ApplicantProfile` established in Stage 21.

```
+----------------------------------------------------------------------------------------------------+
|                                    AUTONOM Desktop (Tauri + React)                                 |
|  [GitHub Portfolio Workspace] <---> [TanStack React Query] <---> [Typed API Client (31 Endpoints)] |
+----------------------------------------------------------------------------------------------------+
                                                |
                                          HTTP / REST
                                                v
+----------------------------------------------------------------------------------------------------+
|                                      FastAPI Backend Service                                       |
|  /api/v1/github/* (Connection, Repos, Architecture, Technologies, Contributions, Candidates, Diag) |
+----------------------------------------------------------------------------------------------------+
                                                |
        +---------------------------------------+---------------------------------------+
        |                                       |                                       |
        v                                       v                                       v
+-----------------------+           +-----------------------+           +-----------------------+
|  GitHubConnectionMgr  |           | RepositoryDiscovery   |           |  ContributionEngine   |
|  - DPAPI Vault Token  |           |  - Public / Org / PAT |           |  - Author vs Committer|
|  - Scope Inspection   |           |  - Manual Ingestion   |           |  - Fork Lineage Eval  |
|  - User Profile Sync  |           |  - Selection Toggles  |           |  - 6-Tier Confidence  |
+-----------------------+           +-----------------------+           +-----------------------+
        |                                       |                                       |
        +---------------------------------------+---------------------------------------+
                                                |
                                                v
                            +---------------------------------------+
                            |       SourceTreeInspector & Fetcher   |
                            |  - Recursive Git Trees (1-API Call)   |
                            |  - < 500 KB Limit & Binary Filtration |
                            |  - SecretRedactor (Zero Cred Leaks)   |
                            +---------------------------------------+
                                                |
                                                v
                            +---------------------------------------+
                            |     Dependency & Tech Classifier      |
                            |  - pyproject, package.json, Cargo, go |
                            |  - Canonical Taxonomy Classification  |
                            |  - ArchitectureAnalyzer (Monorepo/CI) |
                            +---------------------------------------+
                                                |
                                                v
                            +---------------------------------------+
                            |     CandidateReviewManager (HITL)     |
                            |  - Skills & Projects Quarantine Queue |
                            |  - Accept / Modify / Reject Actions   |
                            |  - Promotion into Stage 21 Profile    |
                            +---------------------------------------+
```

---

## 2. Architectural Principles & Boundaries

1. **Zero Silent Mutation**: The system will never write, update, or overwrite applicant skills, projects, or employment history without explicit user confirmation in the desktop review queue.
2. **Strict Read-Only External Access**: AUTONOM never requests write permissions (`repo:write`, `repo:delete`, `workflow`). It will never push commits, merge pull requests, create branches, or modify repository settings.
3. **Local Encryption of Secrets**: All GitHub Personal Access Tokens (PATs) are encrypted using Windows Data Protection API (DPAPI) and AES-256-GCM via `CredentialManager`. Tokens are never exposed in plaintext logs, API responses, or frontend components.
4. **Secret Redaction**: Any retrieved file content, commit message, or snippet is actively scrubbed by `SecretRedactor` to mask private keys, API keys, passwords, and database connection strings before being rendered or stored.
5. **Rate-Limit & Resource Conservation**: GitHub API limits (60 req/hr unauthenticated, 5,000 req/hr authenticated) are protected using recursive tree queries, ETag conditional caching (`304 Not Modified`), and proactive rate-limit metering.

---

## 3. Core Component Subsystems

### 3.1 Connection Management (`app.recruitment.github.auth`)
- **`GitHubConnectionManager`**: Manages the link between the applicant profile and GitHub accounts.
- **Connection Modes**: Supports `PUBLIC_ONLY` (unauthenticated or public profile discovery), `PAT` (fine-grained or classic token for private repos and elevated rate limits), and `MANUAL_URL` (direct inspection of single public repositories).
- **DPAPI Integration**: Stores tokens in the encrypted credential vault and retrieves them ephemerally during active sessions.

### 3.2 Client & Caching Layer (`app.recruitment.github.client`)
- **`GitHubRestClient`**: Asynchronous HTTP client wrapping `httpx.AsyncClient` with explicit headers (`Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28`).
- **`RateLimitController`**: Monitors `x-ratelimit-remaining`, `x-ratelimit-reset`, and `retry-after`. Enforces exponential backoff and prevents secondary rate-limit violations.
- **`ETagCacheManager`**: Stores HTTP ETags for API endpoints. Injects `If-None-Match` on subsequent queries and returns cached responses upon receiving `304 Not Modified`.

### 3.3 Repository Discovery & Source Inspection (`app.recruitment.github.repositories`, `source`)
- **`RepositoryDiscoveryService`**: Queries authenticated user repos, public repos, or org repositories. Normalizes metadata (stars, forks, languages, topics, default branch).
- **`SourceTreeInspector`**: Fetches the complete repository tree using GitHub's recursive Git Data Tree endpoint (`GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1`).
- **`SourceFilter`**: Enforces strict safety boundaries: rejects files $> 500\text{ KB}$, ignores binaries, lockfiles, minified bundles, `.git`, `node_modules`, `vendor/`, and protects against path traversal.
- **`SecretRedactor`**: High-performance regex scanner scrubbing private keys, JWTs, AWS credentials, and database connection strings.

### 3.4 Technology & Architecture Intelligence (`app.recruitment.github.analysis`)
- **`DependencyManifestParser`**: Safe, sandboxed parsing of `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, and `go.mod`.
- **`TechnologyClassifier`**: Maps raw package strings to canonical categories (Framework, Database, ORM, Testing, AI/ML, Containerization).
- **`ArchitectureAnalyzer`**: Determines architectural archetypes (`MONOREPO`, `MICROSERVICE`, `BACKEND_SERVICE`, `FRONTEND_SPA`, `FULLSTACK`, `CLI_TOOL`, `LIBRARY`) and verifies presence of CI workflows, Dockerfiles, and test suites.

### 3.5 Contribution & Attribution Engine (`app.recruitment.github.contributions`)
- **`ContributionAttributionEngine`**: Solves the author vs. committer discrepancy, identifies squash-merge authorship, evaluates pull request reviews, and detects forked upstream lineages.
- **6-Tier Confidence Scale**: Categorizes evidence from `REPOSITORY_ASSOCIATED` up to `INDEPENDENTLY_CORROBORATED`.

### 3.6 Candidate Review & Profile Synchronization (`app.recruitment.github.evidence`)
- **`CandidateGenerator`**: Transforms technical findings and verified contributions into `CandidateSkill` and `CandidateProject` records.
- **`CandidateReviewManager`**: Quarantine queue manager. Upon human acceptance, invokes Stage 21's `ApplicantProfileService.add_or_update_skill()` and `add_project()`, generating immutable verification claims in the `ClaimRegistry`.

---

## 4. Security & Safety Perimeter

| Threat Vector | Mitigation Strategy |
| :--- | :--- |
| **Credential Theft** | Personal Access Tokens are encrypted with Windows DPAPI and AES-256-GCM. Never logged; masked in UI as `ghp_••••••••••••`. |
| **Code Execution Risk** | Downloaded repository source is **never executed**, compiled, or dynamically evaluated. Parsers use static regex and AST/JSON/TOML deserializers. |
| **Secret Leaks** | `SecretRedactor` masks API tokens, RSA keys, and database passwords before they reach desktop UI or persistent state. |
| **Denial of Service (Disk/RAM)** | Strict bounds: maximum 60 candidate files per repo, 500 KB per file, 10 MB total repo memory footprint. |
| **API Rate Limiting** | ETag caching, recursive tree fetching, and proactive rate-limit budget tracking. |
