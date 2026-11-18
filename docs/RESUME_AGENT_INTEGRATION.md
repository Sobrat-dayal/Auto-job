# AUTONOM — Recruitment Agent Integration (Stage 23)

## 1. Multi-Agent Orchestration in Recruitment

AUTONOM's recruitment workflows are executed by autonomous specialist agents collaborating through the Stage 4 Orchestrator:

```
+-------------------------------------------------------------+
|               Recruitment Intelligence Agents               |
+-------------------------------------------------------------+
| 1. Profile Intelligence Specialist (Stage 21)               |
| 2. Repository Intelligence Specialist (Stage 22)            |
| 3. Resume & Tailoring Specialist (Stage 23)                |
| 4. Application Compliance & ATS Specialist (Stage 23)       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                      Task Workflow                          |
|  - Agent receives target job posting                        |
|  - Agent requests tailoring via ResumeService API           |
|  - Tailoring engine matches evidence and scores gaps        |
|  - Agent inspects ATS compliance report                     |
|  - Agent compiles verified PDF artifact                     |
|  - Artifact SHA-256 registered in Audit Ledger              |
+-------------------------------------------------------------+
```

---

## 2. API Surface for Agents

Specialist agents interact with the Resume Intelligence engine using standard REST endpoints:

- `POST /api/v1/job-descriptions/analyze`: Parses job text into structured competencies and requirements.
- `POST /api/v1/resumes`: Creates a fresh resume grounded in the candidate's verified profile.
- `POST /api/v1/resumes/{id}/tailor`: Synthesizes job-aligned sections and prioritized entries.
- `GET /api/v1/resumes/{id}/ats-report`: Retrieves deterministic pass/fail compliance audits.
- `POST /api/v1/resumes/{id}/approve`: Freezes an immutable version snapshot with SHA-256 hash.
- `POST /api/v1/resumes/{id}/export`: Emits native `.docx` or `.pdf` artifacts.

Agents never edit resumes directly via raw strings; they invoke structured endpoints that enforce schema validation and zero-hallucination constraints at every step.
