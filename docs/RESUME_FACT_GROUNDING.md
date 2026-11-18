# AUTONOM — Resume Fact Grounding & Anti-Hallucination Engine (Stage 23)

## 1. Zero Hallucination Protocol

A core vulnerability of LLM-based career tools is "resume hallucination" — generating plausible-sounding achievements, fabricated metrics (e.g. "improved database latency by 45%"), or unverified technologies that the candidate never practiced.

AUTONOM enforces a strict **Zero Hallucination Protocol** through deterministic claim selection and strict provenance validation:

1. **Source Fact Anchoring**:
   Every generated bullet point, summary statement, skill tag, and employment record must anchor to a verified entity in `ApplicantProfile` (Stage 21) or an inspected repository artifact in `GitHubEvidence` (Stage 22).

2. **Claim Verification Status Checks**:
   Unverified claims (marked `VerificationStatus.UNVERIFIED` or lacking supporting evidence) are excluded from high-stakes resume archetypes (`experienced`, `job_tailored`) unless explicitly permitted by the applicant.

3. **Content Verification Pipeline (`ContentValidatorEngine`)**:
   During document compilation and before version approval, `ContentValidatorEngine` scans the synthesized text:
   - Verifies all listed skills exist in the canonical profile skills database.
   - Audits numeric metrics against recorded profile achievements.
   - Checks employment dates against verified institutional records.
   - Raises structured validation warnings or blocks approval if ungrounded statements are detected.

```
+-------------------------------------------------------------+
|                Applicant Profile Claims                     |
|  - Verified Skills: [Python, FastAPI, Docker, PostgreSQL]   |
|  - Verified Achievement: "Reduced p99 query latency by 42%" |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                Content Grounding Verification               |
|  - Skill check: "Kafka" in profile? -> NO                   |
|  - Flag: "Unverified Skill Token: Kafka"                    |
|  - Status: Warning / Requires Review                        |
+-------------------------------------------------------------+
```

---

## 2. Source Fact Reference Structure

When entries are generated, the engine attaches a `SourceFactReference`:
- `source_entity_id`: UUID of the parent `EmploymentRecord`, `ProjectRecord`, or `SkillItem`.
- `claim_id`: UUID of the verified claim in the Stage 21 Claim Registry.
- `verification_status`: Status at time of generation (`user_confirmed`, `evidence_backed`, `externally_verified`).
- `applicant_profile_version`: Version number of the immutable profile snapshot.
- `attribution_level`: Identifies individual, primary, or collaborative contributor status.

This complete provenance chain allows recruiters and automated compliance systems to inspect exactly why each bullet point exists and what evidence supports it.
