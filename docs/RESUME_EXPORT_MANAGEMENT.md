# AUTONOM — Resume Export Management (Stage 23)

## 1. Export Management Subsystem

The **Export Manager** (`ResumeExportManager`) is responsible for compiling, storing, hashing, and serving finished resume files.

```
+-----------------------------------------------------------+
|                   Export Request Payload                  |
|  - format: "pdf" | "docx" | "html" | "json"               |
|  - template_id: "ats_classic"                             |
|  - validate_extraction: true                              |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                   Document Compilation                    |
|  - PDF: PdfResumeRenderer (ReportLab)                     |
|  - DOCX: DocxResumeRenderer (python-docx)                 |
|  - HTML: HtmlPreviewRenderer                              |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|             Round-Trip Machine Validation                 |
|  - Text extraction check (pypdf)                          |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|            Cryptographic Hashing & Storage                |
|  - File written to: data/artifacts/resumes/<id>.<ext>     |
|  - SHA-256 digest computed on generated binary            |
|  - ExportArtifact record registered in DB                 |
+-----------------------------------------------------------+
```

---

## 2. Export Artifact Contract

```python
class ExportArtifact(BaseModel):
    id: str = Field(default_factory=lambda: f"exp_{uuid4().hex[:8]}")
    resume_id: str
    version_id: Optional[str] = None
    format: ExportFormat  # "docx", "pdf", "html", "json"
    template_id: str
    file_path: str
    file_size_bytes: int
    sha256_checksum: str
    extracted_text_snippet: Optional[str] = None
    validation_passed: bool = True
    created_at: datetime
```

---

## 3. Storage Organization

All generated files are written to safe, isolated workspace storage:
- `data/artifacts/resumes/{resume_id}_{version}_{timestamp}.pdf`
- `data/artifacts/resumes/{resume_id}_{version}_{timestamp}.docx`
- `data/artifacts/portfolios/{portfolio_id}_{timestamp}.pdf`
- `data/artifacts/portfolios/{portfolio_id}_{timestamp}.html`

The service streams files with appropriate MIME headers (`application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`) to enable instant downloading and desktop viewing.
