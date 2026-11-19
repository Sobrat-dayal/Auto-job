# Agent Integration & Capabilities (Stage 28)

## 1. Overview
Stage 28 exposes typed internal agent capabilities for the autonomous recruitment agent swarm: `JobDiscoveryAgent`, `JobIntelligenceSpecialist`, `VerificationAgent`, `JobMatchingAgent`, and `Supervisor`.

## 2. Agent Roles
- **Job Discovery Agent**: Automatically triggers intelligence analysis after discovering and aggregating new job vacancies.
- **Job Intelligence Specialist**: Owns the deterministic and AI extraction pipelines, handling qualitative phrasing and complex requirement structures.
- **Verification Agent**: Validates evidence spans, quotation hashes, and ensures zero hallucination.
- **Job Matching Agent**: Consumes read-only structured intelligence records for candidate evaluation (Stage 29).
- **Supervisor**: Orchestrates batch analysis workflows and monitors review queue health.

## 3. Registered Capabilities
| Capability Name | Input | Output | Description |
|---|---|---|---|
| `job.intelligence.analyze` | `canonical_job_id, force, use_ai` | `JobIntelligenceRecord` | Trigger analysis for a single job |
| `job.intelligence.analyze_batch` | `job_ids, use_ai` | `list[JobIntelligenceRecord]` | Trigger analysis for a batch of jobs |
| `job.intelligence.get_record` | `canonical_job_id` | `JobIntelligenceRecord` | Fetch structured intelligence record |
| `job.intelligence.get_requirements` | `canonical_job_id, category` | `list[AtomicRequirement]` | Fetch atomic requirements |
| `job.intelligence.get_skills` | `canonical_job_id` | `list[StructuredSkill]` | Fetch normalized skills |
| `job.intelligence.get_education` | `canonical_job_id` | `list[EducationRequirement]` | Fetch education prerequisites |
| `job.intelligence.get_experience` | `canonical_job_id` | `list[ExperienceRequirement]` | Fetch experience requirements |
| `job.intelligence.get_compensation` | `canonical_job_id` | `CompensationIntelligence` | Fetch compensation intelligence |
| `job.intelligence.get_conditions` | `canonical_job_id` | `EmploymentConditions` | Fetch workplace and schedule terms |
| `job.intelligence.get_deadlines` | `canonical_job_id` | `ApplicationInstructions` | Fetch closing deadlines and instructions |
| `job.intelligence.get_evidence` | `canonical_job_id` | `list[RequirementEvidence]` | Fetch provenance evidence spans |
| `job.intelligence.get_conflicts` | `canonical_job_id` | `list[ConflictRecord]` | Fetch multi-source contradictions |
| `job.intelligence.get_status` | None | `dict` | Fetch operational diagnostics |
