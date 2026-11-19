# Skill Matching Engine

## 1. Skill Resolution Protocol
Matching follows a 4-tier evaluation sequence:
1. **Exact Normalized Match**: Case-insensitive and punctuation-stripped comparison against verified profile skills (`normalize_skill`).
2. **Strict Verified Aliases**: Lookup through an authoritative alias dictionary (e.g. `Postgres` <-> `PostgreSQL`, `TS` <-> `TypeScript`).
   - Strict Anti-Aliases: Negative rules explicitly prevent false mappings (`Java != JavaScript`, `Docker != Kubernetes`, `React != React Native`).
3. **Project & Employment Evidence**: If a skill is absent from explicit profile tags, it is discovered via verified project repositories (Stage 22) or past role technology tags.
4. **Related Technology Families**: Conceptual relatives (e.g. AWS vs GCP, React vs Vue).
   - Classified strictly as `RelatedExperienceOnly`.
   - Never marked as `DirectlySatisfied`.
   - Receives partial credit without creating false claims.

## 2. Tenure Duration Comparison
When an employer mandates a minimum experience tenure (e.g. "Python (5+ years)"):
- If applicant has verified Python experience >= 5.0 years: `DIRECTLY_SATISFIED`.
- If applicant has verified Python experience < 5.0 years: `PARTIALLY_SUPPORTED` with duration deficit gap.
- If applicant has no Python claims: `NOT_EVIDENCED` with blocking gap.
