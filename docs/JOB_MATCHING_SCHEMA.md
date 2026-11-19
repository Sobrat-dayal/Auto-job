# Job Matching Data Schema & Contracts

## 1. Database Entities (SQLite / SQLAlchemy)
- `job_match_evaluations`:
  - `id`: Primary key UUID string.
  - `profile_id`: Foreign key referencing `applicant_profiles.id` (CASCADE).
  - `canonical_job_id`: Foreign key referencing `job_listings.id` (CASCADE).
  - `job_intelligence_id`: Optional reference to Stage 28 intelligence record.
  - `career_strategy_id`: Active strategy ID under which evaluation executed.
  - `rubric_id`: Identifier of weighting rubric utilized (`rubric_default_v1`).
  - `version`: Monotonically incrementing evaluation version integer.
  - `is_current`: Boolean indicating whether evaluation reflects latest profile and job state.
  - `eligibility_outcome`: Structured outcome enum.
  - `relevance_index`: Deterministic float between 0.0 and 100.0.
  - `mandatory_coverage_ratio`: Ratio of satisfied mandatory prerequisites (0.0 to 1.0).
  - `preferred_coverage_ratio`: Ratio of satisfied preferred qualifications (0.0 to 1.0).
  - `evidence_completeness_ratio`: Ratio of non-unknown requirements (0.0 to 1.0).
  - `ranking_uncertainty_ratio`: Ratio of unobserved or unknown inputs (0.0 to 1.0).
  - `application_readiness`: Operational state (`ready_for_preparation`, `requires_review`, `ineligible`).
  - `hard_policy_passed`: Boolean flag.
  - `hard_policy_reason`: Human-readable violation explanation.
  - `score_components_json`: Full dimension breakdown.
  - `gaps_summary_json`: Serialized identified gaps.
  - `input_snapshots_json`: Snapshots of immutable inputs at execution time.
- Child Tables:
  - `job_match_requirement_results`
  - `job_match_logical_group_results`
  - `job_match_gaps`
  - `job_match_review_requests`
  - `job_match_rubrics`
  - `job_match_rankings`
  - `job_match_simulations`
  - `job_match_audit_events`

## 2. Pydantic Contracts
- `JobMatchEvaluation`: Complete evaluation record.
- `RequirementEvaluationResult`: Atomic requirement verdict with evidence citation.
- `GroupEvaluationResult`: 3-valued logical evaluation (`AND`, `OR`, `AtLeastN`).
- `SkillMatchDetail`: In-depth breakdown for skills (exact, alias, related, tenure).
- `EducationMatchDetail`: Degree hierarchy, graduation status, and practical waiver.
- `ExperienceMatchDetail`: Calendar interval math and academic project separation.
- `EligibilityConditionDetail`: Work authorization, sponsorship, and blocklists.
- `SimulationRequest` / `SimulationResponse`: What-If hypothetical execution contracts.
