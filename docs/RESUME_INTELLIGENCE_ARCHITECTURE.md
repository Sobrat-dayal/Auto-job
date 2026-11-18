# AUTONOM — Resume Intelligence Architecture (Stage 23)

## 1. System Overview

The **Resume Intelligence Engine** is the third subsystem of **Phase 5: Recruitment Intelligence Foundation** in AUTONOM. It converts verified, evidence-backed claims from the **Applicant Profile** (Stage 21) and repository intelligence from **GitHub Integration** (Stage 22) into machine-readable, ATS-compliant, professionally formatted resumes and multi-page engineering portfolios.

```
+-----------------------------------------------------------------------------------+
|                            AUTONOM Recruitment Hub                                |
+-----------------------------------------------------------------------------------+
|  Stage 21: Canonical Profile   |  Stage 22: GitHub Intelligence                   |
|  - Verified Claims & Evidence  |  - Repository & Tech Stack Evidence              |
|  - Immutable Profile Snapshots |  - Meaningful Contribution Attribution           |
+--------------------------------+--------------------------------------------------+
                                 |
                                 v
+-----------------------------------------------------------------------------------+
|               Stage 23: Resume Intelligence & Document Engine                     |
+-----------------------------------------------------------------------------------+
|  1. Fact Selection Engine       --> Filters verified claims only (Zero Hallucination)
|  2. Content Generator Engine    --> Deterministic phrasing, action verbs, metrics  |
|  3. Job Tailoring Engine        --> Match matrix, prioritization, gap identification|
|  4. ATS Readability Analyzer    --> 7 Deterministic structural checks (Pass/Warn) |
|  5. Template Engine             --> 6 Professional styling profiles               |
|  6. Dual Document Renderers     --> python-docx (.docx) & ReportLab (.pdf)         |
|  7. Round-Trip Validator        --> pypdf text extraction & section heading audit  |
|  8. Version Manager             --> Immutable snapshots & SHA-256 digests         |
|  9. Portfolio Builder           --> Multi-page project narratives & privacy scrub  |
+-----------------------------------------------------------------------------------+
                                 |
        +------------------------+------------------------+
        v                                                 v
+-----------------------------+               +-----------------------------+
|    Desktop React Frontend   |               |     FastAPI REST Gateway    |
| - 11 Tab Modular Workspace  |               | - 24 High-Performance Routes|
| - Real-time HTML Preview    |               | - Artifact Hash Registry    |
| - Interactive ATS Checklist |               | - Scope-Governed Security   |
+-----------------------------+               +-----------------------------+
```

---

## 2. Core Architectural Principles

1. **Absolute Zero Hallucination Guarantee**:
   The engine never manufactures unearned skills, inflated metrics, phantom employment dates, or unverified technologies. Every bullet point and skill token maps to an underlying verified `SourceFactReference`.

2. **Deterministic, Non-Deceptive ATS Audit**:
   Unlike consumer resume tools that fabricate probabilistic "95% ATS Compatibility Scores", AUTONOM executes an inspectable suite of 7 deterministic structural checks (Single-column layout, machine-readable text, standard section headings, clear chronology, accessible contact info, standard sans/serif typography, clean bullet formatting).

3. **Dual Native Document Renderers**:
   Resumes are compiled directly to Microsoft Word `.docx` via `python-docx` and selectable-text `.pdf` via `ReportLab`. No brittle browser headless print-to-PDF is used for resume compilation.

4. **Automated Round-Trip Validation**:
   Immediately following PDF compilation, `pypdf` extracts the raw text stream and verifies that applicant identity, critical sections, and text contents are 100% extractable by machine readers.

5. **Cryptographic Version Immutability**:
   Once a resume is approved (`DocumentStatus.APPROVED`), its state is frozen into an immutable version snapshot with a SHA-256 digest. Subsequent modifications automatically spawn fresh draft revisions.

6. **Privacy-Preserving Portfolio Synthesis**:
   The portfolio builder highlights technical achievements while filtering out private GitHub repositories, unverified metrics, and sensitive contact details prior to public export.
