# AUTONOM — Resume Template System (Stage 23)

## 1. Professional Templates & Profiles

AUTONOM provides 6 production-grade, ATS-compatible resume templates. Each template definition specifies typography, margins, spacing, section styling, and supported page formats (`letter`, `a4`).

| Template ID | Name | Category | Primary Focus | Best For |
|---|---|---|---|---|
| `ats_classic` | Classic ATS Single-Column | `ats_classic` | Maximum machine readability, clean linear text | Corporate ATS, Taleo, Workday, Greenhouse |
| `modern_professional` | Modern Professional | `modern_professional` | Clean section rules, subtle accent headers | Mid/Senior Engineers, Tech Companies |
| `technical_engineer` | Technical Engineer | `technical_engineer` | Dense skill clustering, project repositories | Systems Engineers, Backend, DevOps |
| `internship_graduate` | Internship / Graduate | `internship_graduate` | Education-first, coursework, academic projects | College Students, Fresh Graduates |
| `academic_cv` | Academic / Research | `academic_research` | Multi-page layout, publications, teaching | PhD candidates, Researchers, Postdocs |
| `minimalist` | Minimalist Monochrome | `minimalist` | Pure typography, high whitespace, no lines | Designers, Executives, Consultants |

---

## 2. Template Definition Schema

Each template is registered as a `ResumeTemplateDefinition` instance in `services/api/app/recruitment/resume/templates/registry.py`:

```python
class ResumeTemplateDefinition(BaseModel):
    id: str
    name: str
    description: str
    category: TemplateCategory
    version: str = "1.0.0"
    supported_page_formats: list[PageFormat]
    supported_sections: list[SectionType]
    primary_font: str
    heading_font: str
    base_font_size_pt: float
    heading_font_size_pt: float
    title_font_size_pt: float
    margin_top_in: float
    margin_bottom_in: float
    margin_left_in: float
    margin_right_in: float
    primary_color: str
    accent_color: str
    text_color: str
    line_spacing: float
    is_two_column: bool = False
    is_ats_optimized: bool = True
```

---

## 3. Strict Layout Constraints for ATS Safety

All templates adhere to ATS engineering guidelines:
- **No Complex Text Boxes**: Text flows strictly in standard document bodies.
- **No Floating Graphics or Canvas Shapes**: Prevents parser coordinate misinterpretation.
- **Standard Heading Naming**: Uses standard uppercase or title case headings recognized by parser dictionaries (`WORK EXPERIENCE`, `EDUCATION`, `TECHNICAL SKILLS`).
- **Standard Safe Fonts**: Helvetica, Arial, Calibri, Times New Roman, Garamond.
