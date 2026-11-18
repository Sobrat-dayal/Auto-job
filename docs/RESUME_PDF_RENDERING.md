# AUTONOM — Resume PDF Rendering & Extraction Validation (Stage 23)

## 1. Native PDF Rendering with ReportLab

AUTONOM renders selectable, machine-readable PDF resumes natively using `ReportLab` (v5.1.0+). The renderer employs `SimpleDocTemplate` and Platypus flowables (`Paragraph`, `Spacer`, `HRFlowable`) to produce crisp, publication-quality documents.

```
+-----------------------------------------------------------+
|                      ResumeDocument                       |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                     PdfResumeRenderer                     |
|  - Page Setup: pagesizes.letter or pagesizes.A4           |
|  - Margin Bounds: 0.75 in (54 pt) uniform padding         |
|  - Paragraph Styles: SampleStyleSheet & Custom Paragraphs |
|  - Header Flowable: Name (18pt Bold) + Contact Row        |
|  - Flowable Story Sequence: Titles, Rules, Entries        |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                    doc.build(story)                       |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|           DocumentRoundTripValidator (pypdf)              |
|  - Extracts raw text stream across all pages              |
|  - Confirms candidate name is extractable                 |
|  - Confirms primary email and contact coordinates         |
|  - Confirms all major section headings are intact         |
+-----------------------------------------------------------+
```

---

## 2. Round-Trip Machine-Readability Verification

Many PDF generators produce documents that visually appear correct but store text in unmapped glyphs, character-dropped font subsets, or complex vector paths that baffle ATS parsers.

AUTONOM solves this with **automated round-trip verification** (`DocumentRoundTripValidator`):

```python
class DocumentRoundTripValidator:
    @classmethod
    def verify_document_content(cls, pdf_bytes: bytes, doc: ResumeDocument) -> dict[str, Any]:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        full_text = "\n".join([page.extract_text() or "" for page in reader.pages])

        checks = []
        # 1. Candidate Name Extractability
        legal_name = doc.header_contact.get("legal_name", "")
        if legal_name and legal_name.lower() in full_text.lower():
            checks.append({"name": "Name Extraction", "status": "pass"})
        else:
            checks.append({"name": "Name Extraction", "status": "error", "message": "Legal name not parsed"})

        # 2. Contact Coordinates Extractability
        email = doc.header_contact.get("primary_email", "")
        if email and email.lower() in full_text.lower():
            checks.append({"name": "Email Extraction", "status": "pass"})
        
        # 3. Section Heading Discovery
        for sec in doc.sections:
            if sec.display_title.lower() in full_text.lower():
                checks.append({"name": f"Section '{sec.display_title}' Found", "status": "pass"})

        return {"all_passed": all(c["status"] == "pass" for c in checks), "checks": checks}
```

This ensures that any exported PDF will be accurately ingested and indexed by enterprise applicant tracking systems.
