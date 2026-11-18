# Cover Letter Design Templates

## AUTONOM Stage 24 — Recruitment Writing Intelligence Engine

---

### Overview

AUTONOM delivers 6 standardized design templates engineered for high readability, ATS text-extraction fidelity, and executive-level visual polish. Each template adheres to strict typographical and spacing standards to ensure that generated DOCX and PDF documents retain perfect single-page layout geometry.

---

### Template Catalog

#### 1. Classic Professional (`classic_professional`)
- **Category**: General & Executive
- **Typography**: Times New Roman (11pt body, 14pt headings, 1.15 line spacing)
- **Palette**: Slate Navy (`#1e293b`), Dark Charcoal (`#0f172a`)
- **Layout Characteristics**: Formal centered header, horizontal separator line, traditional serif typography.
- **ATS Compatibility Score**: 98%

#### 2. Modern Minimalist (`modern_minimalist`)
- **Category**: Contemporary Tech & Startups
- **Typography**: Helvetica / Arial (10.5pt body, 13pt headings, 1.2 line spacing)
- **Palette**: Royal Indigo (`#4f46e5`), Jet Slate (`#1e293b`)
- **Layout Characteristics**: Left-aligned asymmetrical header, clean sans-serif body, generous whitespace, subtle colored accent rules.
- **ATS Compatibility Score**: 99%

#### 3. Technical Engineering (`technical_engineering`)
- **Category**: Software & Systems Engineering
- **Typography**: Consolas / Calibri (10.5pt body, 13pt headings, 1.15 line spacing)
- **Palette**: Cyan Teal (`#0284c7`), Slate Grey (`#334155`)
- **Layout Characteristics**: Structured section headers, monospaced metadata badges, highlighted technical stack callout, bulleted achievement list.
- **ATS Compatibility Score**: 97%

#### 4. Internship & Graduate (`internship_graduate`)
- **Category**: Students & Early Career
- **Typography**: Georgia (10.5pt body, 13pt headings, 1.2 line spacing)
- **Palette**: Emerald Green (`#059669`), Navy Charcoal (`#1e293b`)
- **Layout Characteristics**: Prominent university and degree header block, academic project focus, coursework emphasis.
- **ATS Compatibility Score**: 98%

#### 5. Academic & Research (`academic_research`)
- **Category**: R&D, PhD, Fellowships
- **Typography**: Garamond (11pt body, 14pt headings, 1.25 line spacing)
- **Palette**: Burgundy Plum (`#7e22ce`), Jet Black (`#111827`)
- **Layout Characteristics**: Formal academic layout, bibliographic citation footnotes, extensive research methodologies, grant references.
- **ATS Compatibility Score**: 96%

#### 6. Compact Application Letter (`compact_application`)
- **Category**: High-Volume Tech Applications
- **Typography**: Arial (10pt body, 12pt headings, 1.1 line spacing)
- **Palette**: Steel Slate (`#475569`), Dark Slate (`#0f172a`)
- **Layout Characteristics**: Compact 0.5-inch margins, dense high-signal 3-paragraph format, rapid recruiter scanning layout.
- **ATS Compatibility Score**: 99%

---

### Template Schema Specification

```typescript
export interface CoverLetterTemplateDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  primary_font: string;
  heading_font: string;
  base_font_size_pt: number;
  heading_font_size_pt: number;
  margin_top_in: number;
  margin_bottom_in: number;
  margin_left_in: number;
  margin_right_in: number;
  primary_color: string;
  accent_color: string;
  text_color: string;
  line_spacing: number;
  layout_style: 'classic' | 'modern' | 'compact' | 'academic' | 'technical';
}
```

---

### Document Export Pipeline

1. **DOCX Generation (`python-docx`)**:
   - Custom XML styles applied per template definition.
   - Clean paragraph boundaries avoiding nested text boxes or floating frames that break ATS parsers.
   - Embedded metadata with author, creation timestamp, and SHA-256 content digest.

2. **PDF Generation (`reportlab`)**:
   - Flowable document structure with `SimpleDocTemplate` and custom `ParagraphStyle`.
   - Strict margin clamping based on template specification.
   - Post-generation round-trip text validation using `pypdf`: extracts text from generated PDF and verifies that key tokens (name, target role, company, verified skills) are 100% extractable.
