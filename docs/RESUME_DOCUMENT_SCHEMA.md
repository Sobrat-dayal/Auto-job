# AUTONOM — Resume Document Schema & Contracts (Stage 23)

## 1. Domain Entities & Schemas

The Resume Intelligence engine operates on structured domain models defined in `services/api/app/recruitment/resume/contracts.py` and synchronized with `packages/shared-types/src/resume.ts`.

### 1.1 Resume Archetypes (`ResumeType`)
- `master`: Comprehensive repository of all verified claims and experiences.
- `general`: Balanced profile suitable for standard technical applications.
- `job_tailored`: Dynamically organized and prioritized based on a specific job description.
- `internship`: Prioritizes academic foundation, coursework, and technical projects.
- `experienced`: Highlights professional employment, business metrics, and leadership.
- `academic_cv`: Multi-page focus on publications, research, teaching, and education.
- `minimalist`: Concise, uncluttered representation emphasizing technical stack.

### 1.2 Section Archetypes (`SectionType`)
- `header`: Applicant name, contact coordinates, location, portfolio links.
- `summary`: Role-grounded professional overview synthesized from real experience.
- `experience`: Employment records with verified metric-driven bullet points.
- `education`: Degrees, institutions, graduation dates, coursework, honors.
- `skills`: Categorized technical competencies grouped by domain.
- `projects`: Technical systems with repository links, stack tags, and contribution narratives.
- `certifications`: Industry certifications with issuing organizations and credential IDs.
- `publications`: Scholarly or technical papers, preprints, and talks.
- `awards`: Honors and distinction records.

---

## 2. Core Schema Structures

### `ResumeDocument`
```python
class ResumeDocument(BaseModel):
    id: str = Field(default_factory=lambda: f"res_{uuid4().hex[:8]}")
    owner_id: str
    profile_id: str
    profile_snapshot_id: str
    title: str
    resume_type: ResumeType
    target_role: Optional[str] = None
    job_ref: Optional[str] = None
    template_id: str = "ats_classic"
    page_format: PageFormat = PageFormat.LETTER
    max_pages: int = 1
    header_contact: dict[str, Any]
    sections: list[ResumeSection]
    status: DocumentStatus = DocumentStatus.DRAFT
    current_version: int = 1
    content_hash: str = ""
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
```

### `ResumeSection`
```python
class ResumeSection(BaseModel):
    id: str = Field(default_factory=lambda: f"sec_{uuid4().hex[:8]}")
    section_type: SectionType
    display_title: str
    ordering: int
    is_visible: bool = True
    entries: list[ResumeEntry]
    source_references: list[SourceFactReference]
    validation_state: str = "valid"
```

### `ResumeEntry`
```python
class ResumeEntry(BaseModel):
    id: str = Field(default_factory=lambda: f"ent_{uuid4().hex[:8]}")
    entry_type: str
    title: str
    subtitle: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullet_points: list[str]
    tags: list[str]
    source_refs: list[SourceFactReference]
    metrics: dict[str, Any]
    is_visible: bool = True
    ordering: int = 0
```

### `SourceFactReference`
```python
class SourceFactReference(BaseModel):
    source_entity_id: str
    claim_id: Optional[str] = None
    verification_status: str
    applicant_profile_version: int = 1
    evidence_id: Optional[str] = None
    attribution_level: Optional[str] = None
    source_excerpt: Optional[str] = None
```
