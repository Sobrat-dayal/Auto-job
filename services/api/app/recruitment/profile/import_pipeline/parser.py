"""Safe multi-format document parser (PDF, DOCX, TXT, JSON) for resume and evidence ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from app.recruitment.profile.errors import InvalidDocumentError

logger = logging.getLogger("autonom.recruitment.profile.parser")

MAX_DOCUMENT_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB max
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".json", ".md"}


@dataclass
class ParsedDocument:
    raw_text: str
    content_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentParser:
    """Extracts raw text and structural metadata from authorized resume and portfolio files."""

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def parse_bytes(cls, content: bytes, filename: str) -> tuple[str, str, dict[str, Any]]:
        """Parses in-memory byte buffer and returns (extracted_text, content_hash, metadata)."""
        if len(content) > MAX_DOCUMENT_SIZE_BYTES:
            raise InvalidDocumentError(
                f"File '{filename}' exceeds maximum allowed size ({MAX_DOCUMENT_SIZE_BYTES / (1024 * 1024):.1f} MB)"
            )
        if len(content) == 0:
            raise InvalidDocumentError(f"File '{filename}' is empty")

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise InvalidDocumentError(f"Unsupported file extension '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}")

        content_hash = cls.compute_sha256(content)
        metadata: dict[str, Any] = {
            "filename": filename,
            "extension": ext,
            "size_bytes": len(content),
            "content_hash": content_hash,
            "page_count": 1,
        }

        extracted_text = ""
        try:
            if ext == ".txt" or ext == ".md":
                extracted_text = cls._parse_text(content)
            elif ext == ".json":
                extracted_text, json_meta = cls._parse_json(content)
                metadata.update(json_meta)
            elif ext == ".pdf":
                extracted_text, pdf_meta = cls._parse_pdf(content)
                metadata.update(pdf_meta)
            elif ext == ".docx":
                extracted_text, docx_meta = cls._parse_docx(content)
                metadata.update(docx_meta)
        except InvalidDocumentError:
            raise
        except Exception as exc:
            logger.error(f"Error parsing document '{filename}': {exc}")
            raise InvalidDocumentError(f"Failed to extract text from '{filename}': {exc}") from exc

        clean_text = extracted_text.strip()
        if not clean_text:
            raise InvalidDocumentError(f"No readable text could be extracted from '{filename}'.")

        return clean_text, content_hash, metadata

    @staticmethod
    def _parse_text(content: bytes) -> str:
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                return content.decode(enc)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    @staticmethod
    def _parse_json(content: bytes) -> tuple[str, dict[str, Any]]:
        data = json.loads(content.decode("utf-8"))
        formatted = json.dumps(data, indent=2)
        return formatted, {"json_keys": list(data.keys()) if isinstance(data, dict) else []}

    @staticmethod
    def _parse_pdf(content: bytes) -> tuple[str, dict[str, Any]]:
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        page_count = len(reader.pages)
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            if txt:
                text_parts.append(txt)

        return "\n\n".join(text_parts), {"page_count": page_count}

    @staticmethod
    def _parse_docx(content: bytes) -> tuple[str, dict[str, Any]]:
        import io
        import docx

        doc = docx.Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)

        return "\n".join(paragraphs), {"paragraph_count": len(doc.paragraphs), "table_count": len(doc.tables)}
