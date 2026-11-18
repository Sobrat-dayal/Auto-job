# AUTONOM Recruitment Agent Integration (Stage 21)

## 1. Overview

Stage 21 serves as the authoritative backend for the four recruitment specialist agents established across Phase 5:
1. `JobMatchingAgent` (Stage 23)
2. `ResumeAgent` (Stage 24)
3. `ApplicationAgent` (Stage 25)
4. `InterviewPrepAgent` (Stage 25)

---

## 2. Agent Interfaces & Scoped Queries

### 2.1 JobMatchingAgent
- **Endpoint**: `POST /api/v1/applicants/{profile_id}/snapshot` with `target_agent: "JobMatchingAgent"`
- **Returned Data**:
  - `skills`: Skill names, categories, proficiency levels, years of experience.
  - `location`: City, country, remote preference (`remote_only`, `hybrid`, `flexible`).
  - `experience_overview`: Years of experience, past job titles (anonymized).
  - **Redacted**: Legal name, email, phone number, physical address.
- **Use Case**: Finding matching job postings across automated job boards without exposing candidate identity.

### 2.2 ResumeAgent
- **Endpoint**: `POST /api/v1/applicants/{profile_id}/snapshot` with `target_agent: "ResumeAgent"`
- **Returned Data**:
  - `education`: Institutions, degrees, honors, GPA.
  - `experience`: Employers, roles, employment types, quantifiable achievements, tech stacks.
  - `skills`: Categorized skill lists.
  - `projects`: Technical portfolio highlights.
  - `summary`: Professional executive narrative.
- **Use Case**: Tailoring targeted resumes and cover letters for specific job descriptions based solely on verified achievements.

### 2.3 ApplicationAgent
- **Endpoint**: `POST /api/v1/applicants/{profile_id}/snapshot` with `target_agent: "ApplicationAgent"`
- **Returned Data**:
  - `contact`: Legal name, email, phone, location.
  - `eligibility`: Authorized countries, sponsorship requirements, notice period.
  - Full education and employment records.
- **Security Prerequisite**: Must possess `applicant.eligibility.read` and user must have toggled `confirmed_by_user: true`.
- **Use Case**: Autofilling web forms and ATS application portals via Stage 16 Browser Automation.

### 2.4 InterviewPrepAgent
- **Endpoint**: `POST /api/v1/applicants/{profile_id}/snapshot` with `target_agent: "InterviewPrepAgent"`
- **Returned Data**:
  - `projects`: Architectures, technologies, author contributions, repository links.
  - `experience`: Responsibilities, challenges, and measurable results.
- **Use Case**: Generating realistic mock interview questions, behavioral scenarios, and technical deep-dives.

---

## 3. Stage 15 Memory Invalidation (`ProfileMemorySync`)

When canonical profile records are edited (e.g., a skill updated or an employment record added), `ProfileMemorySync` dispatches an `applicant.memory_invalidated` event across the central event bus:
- Outdated vector embeddings in Stage 15 episodic memory are flagged for re-indexing.
- Prevents cached agent prompts from using superseded or deleted career facts.
