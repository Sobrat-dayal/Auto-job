# AUTONOM Applicant Profile Architecture (Stage 21)

## 1. Overview and Mission

Stage 21 establishes the foundational **authoritative applicant identity and verified professional profile system** for the AUTONOM Windows 11 autonomous desktop platform, inaugurating **Phase 5: Recruitment Intelligence Foundation**.

Before Stage 21, AUTONOM established:
- Real local and cloud AI inference (Stages 11–13)
- Multi-agent orchestration and Supervisor (Stage 14)
- Granular authorization and safety enforcement (Stage 14)
- Persistent semantic and procedural memory (Stage 15)
- Multi-method browser, Windows structural, and visual automation (Stages 16–20)

Stage 21 provides downstream recruitment specialist agents (`JobMatchingAgent`, `ResumeAgent`, `ApplicationAgent`, `InterviewPrepAgent`) with an immutable, verified **Single Source of Truth** for applicant qualifications, work history, skills, and legal attestations, guaranteeing **zero hallucination**, explicit human review of extracted claims, cryptographic evidence provenance, and scoped PII redaction.

---

## 2. High-Level System Architecture

```mermaid
flowchart TD
    subgraph ImportLayer["1. Secure Ingestion & Parsing"]
        DocInput["Resume / CV / Transcript (PDF, DOCX, TXT, JSON)"]
        Parser["DocumentParser (SHA-256 Digest, Magic Byte Validation)"]
        Extractor["CandidateExtractor (Heuristic & AI Candidate Extractor)"]
        ReviewQueue["Human Review Queue (CandidateReviewQueue)"]
    end

    subgraph CoreEngine["2. Authoritative Profile & Claim Engine"]
        ProfileService["ApplicantProfileService (Central Facade)"]
        ClaimReg["ClaimRegistry (Atomic Claims, Provenance, Conflict Engine)"]
        QualityEngine["DataQualityEngine (Deterministic Scoring, Completeness)"]
        Vault["EvidenceVault (Encrypted Local Storage, SHA-256 Fingerprinting)"]
    end

    subgraph SecurityAndIntegrations["3. Scoped Adapters & Downstream Agents"]
        AuthEnforcer["ProfileAuthorizationEnforcer (Scope Enforcement)"]
        AgentAdapter["AgentProfileAdapter (Scoped Snapshot Generators)"]
        MemSync["ProfileMemorySync (Stage 15 Event Bus & Invalidation)"]
        JobAgent["JobMatchingAgent (Contact PII Redacted)"]
        ResumeAgent["ResumeAgent (Sanitized Professional Data)"]
        AppAgent["ApplicationAgent (Legal & Eligibility Authorized)"]
        PrepAgent["InterviewPrepAgent (Projects & Tech Stack Scoped)"]
    end

    DocInput --> Parser
    Parser --> Extractor
    Extractor --> ReviewQueue
    ReviewQueue -->|User Approves / Modifies| ProfileService

    ProfileService <--> ClaimReg
    ProfileService <--> QualityEngine
    ProfileService <--> Vault
    ProfileService --> MemSync

    ProfileService --> AuthEnforcer
    AuthEnforcer --> AgentAdapter
    AgentAdapter --> JobAgent
    AgentAdapter --> ResumeAgent
    AgentAdapter --> AppAgent
    AgentAdapter --> PrepAgent
```

---

## 3. Core Architectural Principles

### 3.1 Single Source of Truth
All applicant facts originate from `ApplicantProfileService`. No recruitment agent is permitted to fabricate, assume, or synthesize unverified credentials, dates, or contact info.

### 3.2 Human-in-the-Loop Review Queue
Candidate claims parsed from uploaded resumes or external platforms remain in an `AWAITING_REVIEW` holding state. Only explicit user acceptance or modification transitions extracted entities into the canonical profile.

### 3.3 Evidence-Backed Provenance
Every atomic claim is tied to supporting documents stored in the local evidence vault, hashed via SHA-256 to ensure data integrity and tamper detection.

### 3.4 Scoped Privacy and Zero PII Leakage
Each downstream specialist agent receives only the subset of data permitted by its authorization policy:
- `JobMatchingAgent`: Skills, preferred roles, geographic locations, work arrangements. **Contact info (name, email, phone) is strictly omitted/redacted.**
- `ResumeAgent`: Full employment history, achievements, and degrees.
- `ApplicationAgent`: Authorized countries, work eligibility, and necessary contact coordinates for submission.
- `InterviewPrepAgent`: Project descriptions, technologies used, and architecture talking points.

### 3.5 Optimistic Concurrency and Immutable Audit History
Profile updates increment an integer `version` field. Mutating requests evaluate `expected_version` against the current profile state. Concurrent collisions trigger `ConcurrencyConflictError` (HTTP 409). Every change is persisted to `ProfileVersionRecord`.
