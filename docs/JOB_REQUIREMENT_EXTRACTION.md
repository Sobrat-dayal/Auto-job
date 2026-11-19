# Job Requirement Extraction & Normalization (Stage 28)

## 1. Overview
The Requirement Extraction subsystem segments raw job descriptions into structured sections, parses atomic qualifications, maps terms against canonical taxonomies, and enforces strict boundary rules between duties and prerequisites.

## 2. Structural Section Segmentation
Raw descriptions are normalized into plain text and partitioned into standard sections:
- `MINIMUM_QUALIFICATIONS`: Minimum requirements, must haves, basic qualifications, what you'll bring.
- `PREFERRED_QUALIFICATIONS`: Nice to haves, bonuses, pluses, preferred requirements.
- `RESPONSIBILITIES`: Day-to-day duties, role mission, what you'll do.
- `COMPENSATION`: Salary ranges, pay rates, base/bonus/equity information.
- `BENEFITS`: 401(k), healthcare, PTO, learning stipends, wellness programs.
- `HOW_TO_APPLY`: Deadlines, application URLs, required materials.
- `EEO_LEGAL`: Equal opportunity statements, legal disclosures.

## 3. Mandatory vs. Preferred Boundary Enforcement
A critical invariant of the AUTONOM intelligence engine is:
- Skills or qualifications under `MINIMUM_QUALIFICATIONS` default to `RequirementCategory.MANDATORY`.
- Skills or qualifications under `PREFERRED_QUALIFICATIONS` default to `RequirementCategory.PREFERRED`.
- **Under no circumstances is a preferred qualification promoted to mandatory.**
- Skills mentioned exclusively in `RESPONSIBILITIES` are categorized as `RequirementCategory.INFORMATIONAL` and are not treated as strict gating prerequisites.

## 4. Extraction Pipeline
1. Preprocess raw HTML, unescaping HTML entities and converting structural tags into bullets (`•`) and standard newlines.
2. Segment text into sections with character start and end offsets.
3. Apply canonical taxonomy matchers for programming languages, frameworks, cloud, databases, and AI/ML.
4. Extract numeric experience durations associated with each skill.
5. Parse degree levels, fields of study, and practical equivalencies.
6. Verify supporting quote spans using the Hallucination Defense pipeline.
