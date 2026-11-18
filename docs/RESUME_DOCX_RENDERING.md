# AUTONOM — Resume DOCX Rendering (Stage 23)

## 1. Native Word Document Generation Architecture

AUTONOM utilizes `python-docx` to generate genuine Microsoft Word `.docx` documents directly from structured `ResumeDocument` models without intermediate HTML or browser printing layers.

```
+-----------------------------------------------------------+
|                      ResumeDocument                       |
|   (Header Contact, Sections, Entries, Bullets, Tags)      |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                    DocxResumeRenderer                     |
|  - Page Setup: Letter / A4 margins (0.75 in)              |
|  - Font Styles: Primary Body (10pt), Heading 1 (12pt Bold)|
|  - Document Title & Contact Subtitle Rendering            |
|  - Section Heading Rules & Spacing Before/After           |
|  - Bullet List Construction (List Bullet style)           |
|  - Metadata Injection: Core Properties (Title, Author)    |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|               Verified .docx Binary Output                |
|             (Native OpenXML Document Stream)              |
+-----------------------------------------------------------+
```

---

## 2. OpenXML Document Structure Details

### 2.1 Margins & Geometry
The renderer sets uniform section margins based on the chosen template:
```python
section = doc.sections[0]
section.top_margin = Inches(template.margin_top_in)
section.bottom_margin = Inches(template.margin_bottom_in)
section.left_margin = Inches(template.margin_left_in)
section.right_margin = Inches(template.margin_right_in)
```

### 2.2 Section Headings
Headings are emitted with uppercase text and styled using template accent colors:
```python
h = doc.add_paragraph()
run = h.add_run(sec.display_title.upper())
run.font.name = template.heading_font
run.font.size = Pt(template.heading_font_size_pt)
run.font.bold = True
h.paragraph_format.space_before = Pt(8)
h.paragraph_format.space_after = Pt(3)
h.paragraph_format.keep_with_next = True
```

### 2.3 Bullet Formatting
Bullet points use the built-in Word style `'List Bullet'` with calibrated line spacing:
```python
p = doc.add_paragraph(style='List Bullet')
p.paragraph_format.space_after = Pt(2)
p.paragraph_format.line_spacing = template.line_spacing
p.add_run(bullet_text)
```

This guarantees that Word documents open cleanly in desktop Word, LibreOffice, and Google Docs, and parse reliably when uploaded to enterprise ATS portals.
