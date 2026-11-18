# AUTONOM — Job-Specific Resume Tailoring (Stage 23)

## 1. Tailoring Methodology & Architecture

The **Job Tailoring Engine** aligns candidate resumes to target job descriptions while strictly upholding the Zero Hallucination Guarantee. It never fabricates missing skills to match a job posting.

```
+---------------------------------------------------------------------------------+
|                               Job Description Raw Text                          |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       1. Job Description Parser                                 |
|  - Title & Employer Extraction                                                  |
|  - Required Skills vs. Preferred Skills Identification                          |
|  - Experience & Education Constraint Extraction                                 |
|  - Responsibility Pattern Analysis                                              |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                   2. Evidence Matching Engine (Match Matrix)                    |
|  - Directly Supported: Candidate has verified evidence for required skill       |
|  - Partially Supported: Skill in related domain with partial evidence           |
|  - Related Domain: Conceptual familiarity evidenced through related projects    |
|  - Not Evidenced: Required skill missing from profile -> Flagged transparently  |
|  - Requires Review: Skill mentioned in unverified claim                         |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                   3. Section & Entry Prioritization Engine                      |
|  - Reorders project entries to showcase systems matching job requirements       |
|  - Prioritizes relevant skill categories and keyword visibility                 |
|  - Generates transparent qualification match breakdown for the applicant        |
+---------------------------------------------------------------------------------+
```

---

## 2. Requirement Matching Categories

Each requirement identified in the job posting is classified into one of five deterministic buckets:

1. **Directly Supported**:
   The skill or qualification is explicitly present in the applicant's verified profile and backed by evidence (e.g., project repo, certification, employment bullet).
2. **Partially Supported**:
   The applicant has evidenced a direct ancestor or core component of the technology (e.g., strong Python experience when FastAPI is requested).
3. **Related Domain**:
   The applicant possesses competencies in an equivalent architectural domain (e.g., PostgreSQL experience when MySQL is requested).
4. **Not Evidenced**:
   The requirement is not found anywhere in the candidate's verified profile. AUTONOM clearly reports this as an honest gap rather than fabricating knowledge.
5. **Requires Review**:
   The claim exists in the profile but is pending user confirmation or external evidence.

---

## 3. Prioritization Strategy

When tailoring a resume:
- Relevant projects that utilize the target tech stack are promoted to the top of the projects section.
- Relevant employment bullets are reordered to emphasize required responsibilities.
- The professional summary highlights target competencies shared between the candidate and the job description.
