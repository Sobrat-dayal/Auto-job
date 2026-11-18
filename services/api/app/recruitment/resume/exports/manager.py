"""Central Export & Document Artifact Management Engine (Stage 23)."""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4
from app.core.config import settings
from app.recruitment.resume.contracts import (
    ExportArtifact,
    ExportFormat,
    ResumeDocument,
    ResumeExportRequest,
)
from app.recruitment.resume.errors import DocumentExportError
from app.recruitment.resume.renderers.docx_renderer import DocxRenderer
from app.recruitment.resume.renderers.pdf_renderer import PdfRenderer
from app.recruitment.resume.renderers.validation import DocumentRoundTripValidator
from app.recruitment.resume.templates.registry import ResumeTemplateRegistry

logger = logging.getLogger("autonom.recruitment.resume.exports.manager")


class ExportManager:
    """Manages physical document compilation, cryptographic checksumming, and export auditing."""

    def __init__(self) -> None:
        self._exports: dict[str, ExportArtifact] = {}

    def list_exports(self, resume_id: Optional[str] = None) -> list[ExportArtifact]:
        if resume_id:
            return [e for e in self._exports.values() if e.resume_id == resume_id]
        return list(self._exports.values())

    def get_export(self, export_id: str) -> ExportArtifact:
        exp = self._exports.get(export_id)
        if not exp:
            raise DocumentExportError(f"Export artifact '{export_id}' not found.")
        return exp

    def export_resume(
        self,
        doc: ResumeDocument,
        req: ResumeExportRequest,
    ) -> ExportArtifact:
        template = ResumeTemplateRegistry.get_template(doc.template_id)

        # 1. Generate Safe Filename
        name = doc.header_contact.get("legal_name") or "Applicant"
        clean_name = re.sub(r"[^\w\-_]", "_", name)
        role = re.sub(r"[^\w\-_]", "_", doc.target_role or doc.title)
        ext = "docx" if req.format == ExportFormat.DOCX else "pdf"

        filename = req.custom_filename or f"Resume_{clean_name}_{role}_v{doc.current_version}.{ext}"

        # 2. Resolve Output Path
        artifacts_dir = Path(getattr(settings, "artifacts_dir", settings.data_dir / "artifacts")) / "resumes"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        file_path = str(artifacts_dir / filename)

        # 3. Render
        if req.format == ExportFormat.DOCX:
            DocxRenderer.render_to_file(doc, template, file_path)
        elif req.format == ExportFormat.PDF:
            PdfRenderer.render_to_file(doc, template, file_path)
        else:
            raise DocumentExportError(f"Unsupported resume export format: {req.format}")

        # 4. Compute Checksum & File Size
        p = Path(file_path)
        content_bytes = p.read_bytes()
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        file_size = len(content_bytes)

        # 5. Round-trip Extraction Validation
        validation_res = None
        if req.validate_extraction:
            if req.format == ExportFormat.DOCX:
                extracted = DocumentRoundTripValidator.extract_text_from_docx(file_path)
            else:
                extracted = DocumentRoundTripValidator.extract_text_from_pdf(file_path)

            validation_res = DocumentRoundTripValidator.verify_document_content(extracted["full_text"], doc)
            validation_res["extracted_word_count"] = len(extracted["full_text"].split())

        artifact = ExportArtifact(
            resume_id=doc.id,
            version_id=str(doc.current_version),
            format=req.format,
            filename=filename,
            file_path=file_path,
            file_size_bytes=file_size,
            sha256_checksum=sha256,
            status="completed",
            validation_result=validation_res,
        )

        self._exports[artifact.export_id] = artifact
        logger.info(f"Completed {req.format.value.upper()} export: {artifact.export_id} ({filename}, {file_size} bytes)")
        return artifact

