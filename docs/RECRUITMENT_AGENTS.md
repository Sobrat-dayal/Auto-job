# AUTONOM — Recruitment Specialist Agents Architecture

## 1. Overview

Recruitment is AUTONOM's primary operational focus. Stage 13 implements the complete set of **6 recruitment specialist agents**, establishing end-to-end multi-agent pipelines for job discovery, requirement analysis, qualification matching, resume tailoring, application field classification, recruiter communication, and interview coaching.

```
       [Raw Job Search / URL / Text]
                     |
                     v
       +-----------------------------+
       |   Job Discovery Agent       | -> Normalizes & parses structured criteria
       +--------------+--------------+
                      |
                      v
       +-----------------------------+
       |     Job Matching Agent      | -> Compares against applicant profile
       +--------------+--------------+
                      |
                      v (Match Score >= Threshold)
       +-----------------------------+
       |   Resume & Tailoring Agent  | -> Generates verified LaTeX / text bullets
       +--------------+--------------+
                      |
         +------------+------------+
         |                         |
         v                         v
+------------------+     +-------------------+
|Application Agent |     |Interview Prep Agt |
|Field Classifier  |     |STAR Q&A Generator |
+------------------+     +-------------------+
         |
         v
+------------------------+
|Recruitment Comms Agent |
|Recruiter Reply Drafter |
+------------------------+
```

---

## 2. The 6 Recruitment Specialists

### 2.1 Job Discovery Agent (`job_discovery_agent`)
- **Category**: Recruitment | **Availability**: Limited (Local parsing operational; live external scrapers planned)
- **Role**: Normalizes raw job listings, cleans HTML/markdown text, extracts structured compensation ranges, remote status, location, and technical requirements.
- **Key Capabilities**:
  - `recruitment_parse_search_criteria`: Converts free-form search queries into structured filters.
  - `recruitment_normalize_job_listing`: Cleans messy job postings into standardized JSON schemas.

### 2.2 Job Matching Agent (`job_matching_agent`)
- **Category**: Recruitment | **Availability**: Operational
- **Role**: Performs deep semantic skill comparison between verified candidate profile attributes and extracted job requirements.
- **Key Capabilities**:
  - `recruitment_extract_job_requirements`: Identifies required vs. preferred technologies, education, and years of experience.
  - `recruitment_match_skills`: Computes match percentages, matched skills, missing skills, and overall qualification score.

### 2.3 Resume & Tailoring Agent (`resume_agent`)
- **Category**: Recruitment | **Availability**: Operational
- **Role**: Synthesizes targeted resume experience bullets using the candidate's verified employment history.
- **Key Capabilities**:
  - `recruitment_draft_resume_bullets`: Generates impactful, quantified accomplishment statements aligned with specific target skills.
- **Anti-Hallucination Policy**:
  - The agent is constrained by its system prompt and verifier contract to **never invent qualifications, companies, or metrics**.
  - All bullets must be grounded in verified candidate career milestones.

### 2.4 Application Agent (`application_agent`)
- **Category**: Recruitment | **Availability**: Limited (Field mapping operational; live form submission planned)
- **Role**: Classifies ATS application fields (e.g., Workday, Greenhouse, Lever) and maps verified user profile values to form inputs.
- **Key Capabilities**:
  - `recruitment_classify_application_fields`: Categorizes input types, required status, and autofill strategies.

### 2.5 Recruitment Comms Agent (`recruitment_comms_agent`)
- **Category**: Recruitment | **Availability**: Limited (Email drafting operational; SMTP sending planned)
- **Role**: Analyzes recruiter correspondence, summarizes dialogue history, and drafts professional, context-aware email replies.
- **Key Capabilities**:
  - `recruitment_summarize_conversation`: Synthesizes email threads and notes key topics and next steps.
  - `recruitment_draft_recruiter_reply`: Generates polite interview confirmations, availability notes, or salary inquiries.

### 2.6 Interview Prep Agent (`interview_prep_agent`)
- **Category**: Recruitment | **Availability**: Operational
- **Role**: Generates comprehensive behavioral and technical interview preparation kits based on the target job description and applicant profile.
- **Key Capabilities**:
  - `recruitment_generate_interview_questions`: Creates targeted STAR-method interview questions, evaluation criteria, and recommended talking points.

---

## 3. End-to-End Collaboration Pipeline

During the Stage 13 verification suite, the recruitment multi-agent collaboration workflow was tested end-to-end:

1. **Job Analysis Stage**:
   - `job_matching_agent` extracted requirements from a Senior Python & Distributed Systems role (Python, FastAPI, Kubernetes, Redis, Docker).
2. **Matching Stage**:
   - `job_matching_agent` computed an 80% qualification match against the applicant's profile (highlighting Python, FastAPI, Docker, and Redis as matches; Kubernetes as a gap).
3. **Tailoring Stage**:
   - `resume_agent` drafted 4 quantified accomplishment bullets addressing the matched skills.
4. **Verification Stage**:
   - `verifier` validated the schema, checked for non-empty bullets, and verified that no unauthorized credentials were leaked.

All steps completed successfully in a fully automated, deterministic DAG execution.
