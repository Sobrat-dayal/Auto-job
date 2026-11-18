# AUTONOM Applicant Skills & Technical Projects (Stage 21)

## 1. Skills Taxonomy & Normalization

To enable reliable job matching and resume tailoring without hallucinations, Stage 21 implements a structured skill taxonomy.

### 1.1 Canonical Normalization
Every skill entered or extracted is mapped to:
- `name`: Human-readable label (e.g., "Kubernetes", "Amazon Web Services (AWS)").
- `canonical_name`: Normalized lowercase identifier (e.g., "kubernetes", "aws").
- `category`: Strict categorization (`SkillCategory`):
  - `programming_languages` (Python, Rust, Go, TypeScript, C++, Java, etc.)
  - `frameworks_libraries` (React, Next.js, FastAPI, Django, PyTorch, etc.)
  - `cloud_devops` (AWS, GCP, Azure, Docker, Kubernetes, Terraform, CI/CD)
  - `databases` (PostgreSQL, MySQL, Redis, MongoDB, SQLite)
  - `ai_ml` (Scikit-Learn, PyTorch, TensorFlow, LLMs, LangChain)
  - `testing` (PyTest, Playwright, Vitest, Jest)
  - `development_tools` (Git, Linux, Vim, Docker Compose)
  - `soft_skills` (Leadership, Mentorship, Communication)

### 1.2 Proficiency and Experience
- `proficiency`: `beginner`, `intermediate`, `advanced`, `expert`.
- `years_experience`: Numeric years practiced.
- `last_used`: Year last actively practiced.

---

## 2. Technical Projects Portfolio

### 2.1 Project Schema
- `title`: Project name.
- `description`: Architectural problem statement and solution.
- `category`: `personal`, `academic`, `open_source`, `commercial`.
- `technologies`: Stack components leveraged.
- `applicant_contribution`: Specific authored modules, algorithms, and infrastructure.
- `team_context`: Solo project vs team size and role.
- `repo_url`: Public or private repository URL (e.g. GitHub, GitLab).
- `live_url`: Deployed system or demo URL.
- `results`: Quantifiable outcomes (e.g., "500+ GitHub stars", "Processed 10M records/day").
- `verification_status`: Status of proof (code repo, live link, publication).

### 2.2 Integration with Interview Prep Agent
When `InterviewPrepAgent` requests a scoped snapshot:
- Contact information is completely omitted.
- Only project descriptions, applicant contribution details, technical challenges, and stack components are provided.
- This equips the agent to generate targeted technical interview questions and scenario drills without exposing sensitive personal coordinates.
