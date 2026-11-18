# AUTONOM — Resume Content Generation (Stage 23)

## 1. Professional Content Generation Engine

The content generation subsystem transforms raw profile data into high-impact, professional resume copy without hallucination. It is composed of four specialized engines:

### 1.1 Fact Selection Engine (`FactSelectionEngine`)
- Analyzes candidate background and determines the optimal section ordering:
  - **Internship / Graduate**: `Summary -> Education -> Projects -> Skills -> Experience -> Certifications`.
  - **Experienced / Job Tailored**: `Summary -> Experience -> Skills -> Projects -> Education -> Certifications`.
  - **Academic / CV**: `Summary -> Education -> Publications -> Experience -> Projects -> Skills`.
- Filters eligible experiences, technical projects, and skills based on target role relevance.

### 1.2 Professional Summary Generator (`ProfessionalSummaryGenerator`)
Synthesizes concise, 2-3 sentence executive summaries tailored to the applicant's experience level:
- **Experienced Archetype**: Identifies primary discipline, years of experience, top verified technical competencies, and standout engineering achievements.
- **Internship / Graduate Archetype**: Highlights degree in progress, core academic discipline, verified technical foundations, and project experience.
- **Job-Tailored Archetype**: Aligns candidate's verified skills with the specific focus areas of the target role.

### 1.3 Experience Bullet Engine (`ExperienceBulletEngine`)
Transforms job descriptions and achievement records into executive bullet points:
- Begins with strong, active verbs in the past tense (e.g., *Architected*, *Engineered*, *Implemented*, *Optimized*, *Spearheaded*).
- Integrates quantitative metrics directly from verified records:
  - Metric values, percentages, or units (e.g., "Reduced p99 latency by 42%").
- Contextualizes responsibilities with tech stack keywords.
- Restricts bullets to 3-5 concise, scannable statements per employment position.

### 1.4 Skills Organization Engine (`SkillsOrganizationEngine`)
Transforms flat skill lists into clean, categorized clusters:
- **Languages**: Python, Rust, TypeScript, Go, C++.
- **Frameworks & Libraries**: FastAPI, React, Node.js, PyTorch.
- **Databases & Storage**: PostgreSQL, Redis, MongoDB, Elasticsearch.
- **Cloud & DevOps**: AWS, Docker, Kubernetes, CI/CD GitHub Actions.
- **Tools & Protocols**: Git, Linux, REST, gRPC, WebSockets.

This structure allows ATS parsers and human recruiters to immediately scan technical qualifications by domain.
