"""Document Verification & Text Extraction Round-Trip Validator (Stage 23)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
import docx
import pypdf
from app.recruitment.resume.contracts import ResumeDocument, SectionType
from app.recruitment.resume.errors import DocumentExportError

logger = logging.getLogger("autonom.recruitment.resume.renderers.validation")


class DocumentRoundTripValidator:
    """Reopens exported DOCX and PDF files to verify physical integrity, text extractability, and factual completeness."""

    @classmethod
    def extract_text_from_pdf(cls, file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise DocumentExportError(f"PDF file does not exist: {file_path}")

        reader = pypdf.PdfReader(str(path))
        num_pages = len(reader.pages)
        full_text = ""
        page_texts = []

        for p_idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            page_texts.append(txt)
            full_text += f"\n--- Page {p_idx + 1} ---\n" + txt

        return {
            "format": "pdf",
            "page_count": num_pages,
            "full_text": full_text.strip(),
            "page_texts": page_texts,
            "has_extractable_text": len(full_text.strip()) > 50,
            "file_size_bytes": path.stat().st_size,
        }

    @classmethod
    def extract_text_from_docx(cls, file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise DocumentExportError(f"DOCX file does not exist: {file_path}")

        doc = docx.Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)

        return {
            "format": "docx",
            "paragraph_count": len(paragraphs),
            "full_text": full_text.strip(),
            "has_extractable_text": len(full_text.strip()) > 50,
            "file_size_bytes": path.stat().st_size,
        }

    @classmethod
    def verify_document_content(
        cls,
        extracted_text: str,
        doc: ResumeDocument,
    ) -> dict[str, Any]:
        """Compares extracted text against critical canonical fields."""
        checks = []
        text_lower = extracted_text.lower()

        # 1. Name Check
        name = doc.header_contact.get("legal_name") or doc.title
        name_present = name.lower() in text_lower
        checks.append({
            "field": "legal_name",
            "expected": name,
            "passed": name_present,
        })

        # 2. Section Titles Check
        for sec in doc.sections:
            if sec.is_visible and sec.entries:
                sec_passed = sec.display_title.lower() in text_lower
                checks.append({
                    "field": f"section_{sec.section_type.value}",
                    "expected": sec.display_title,
                    "passed": sec_passed,
                })

        # 3. Entry Titles Check
        missing_entries = []
        for sec in doc.sections:
            if sec.is_visible:
                for entry in sec.entries:
                    if entry.title.lower() not in text_lower:
                        missing_entries.append(entry.title)

        checks.append({
            "field": "entries_presence",
            "missing_entries": missing_entries,
            "passed": len(missing_entries) == 0,
        })

        all_passed = all(c.get("passed", False) for c in checks)
        return {
            "all_passed": all_passed,
            "checks": checks,
        }
