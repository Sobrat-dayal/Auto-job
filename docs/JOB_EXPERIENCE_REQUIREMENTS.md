# Experience Requirements & Duration Analysis (Stage 28)

## 1. Overview
The Experience Extraction module analyzes professional tenure prerequisites, minimum and maximum duration bounds, and domain-specific specializations.

## 2. Extraction Logic
The engine recognizes varied phrasings of experience ranges:
- Single lower bound: `"5+ years of software engineering experience"` -> `min_years = 5.0, max_years = None`.
- Closed range: `"3-5 years of backend engineering"` -> `min_years = 3.0, max_years = 5.0`.
- Minimum qualifier: `"At least 7 years experience with distributed systems"` -> `min_years = 7.0, max_years = None`.
- Entry-level waiver: `"No prior professional experience required"` -> `min_years = 0.0, max_years = 0.0, is_mandatory = False`.

## 3. Domain Specializations
Extracted domain categories:
- `Backend Development`: APIs, microservices, databases, server architectures.
- `Frontend Development`: Web interfaces, UI/UX, browser runtime.
- `Full-Stack Development`: End-to-end web applications.
- `Distributed Systems`: Consensus, clustering, replication, high-availability storage.
- `Machine Learning & AI`: Training, evaluation, NLP, computer vision, inference pipelines.
- `Cloud Architecture & DevOps`: Infrastructure as code, Kubernetes, CI/CD, cloud platforms.
- `Security & SRE`: Incident response, reliability, zero-trust architectures.

## 4. Provenance Binding
Every parsed experience requirement binds directly to a verified `RequirementEvidence` record with source span offsets and SHA-256 quotation hash.
