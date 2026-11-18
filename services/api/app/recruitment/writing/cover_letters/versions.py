"""Cover Letter Versioning & Immutability Manager (Stage 24)."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4
from app.recruitment.writing.contracts import (
    CoverLetterDocument,
    CoverLetterVersionRecord,
    WritingDocumentStatus,
)
from app.recruitment.writing.errors import CoverLetterNotFoundError

logger = logging.getLogger("autonom.recruitment.writing.cover_letters.versions")


class CoverLetterVersionManager:
    """Manages immutable snapshots and cryptographic content digests for approved cover letters."""

    def __init__(self) -> None:
        self._versions: dict[str, list[CoverLetterVersionRecord]] = {}

    @staticmethod
    def compute_content_hash(doc: CoverLetterDocument) -> str:
        """Computes a deterministic SHA-256 digest over normalized cover letter content blocks."""
        payload = {
            "title": doc.title,
            "target_role": doc.target_role,
            "employer_name": doc.employer_name,
            "blocks": [{"type": b.block_type, "text": b.text.strip(), "ordering": b.ordering} for b in doc.blocks],
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def snapshot_version(
        self,
        doc: CoverLetterDocument,
        actor_id: str = "default_user",
        changelog: str = "Approved cover letter snapshot",
    ) -> CoverLetterVersionRecord:
        content_hash = self.compute_content_hash(doc)
        doc.content_hash = content_hash
        doc.status = WritingDocumentStatus.APPROVED
        doc.approved_at = datetime.now(UTC)

        record = CoverLetterVersionRecord(
            cover_letter_id=doc.id,
            version_number=doc.current_version,
            profile_snapshot_id=doc.profile_snapshot_id,
            content_hash=content_hash,
            changelog=changelog,
            actor_id=actor_id,
            is_published=True,
            document_snapshot=doc.model_dump(),
        )

        if doc.id not in self._versions:
            self._versions[doc.id] = []
        self._versions[doc.id].append(record)

        logger.info(f"Snapshotted CoverLetter '{doc.id}' v{doc.current_version} (SHA256: {content_hash[:12]}...)")
        return record

    def list_versions(self, cover_letter_id: str) -> list[CoverLetterVersionRecord]:
        return list(self._versions.get(cover_letter_id, []))

    def get_version(self, cover_letter_id: str, version_number: int) -> Optional[CoverLetterVersionRecord]:
        versions = self._versions.get(cover_letter_id, [])
        for v in versions:
            if v.version_number == version_number:
                return v
        return None

    def restore_version(self, cover_letter_id: str, version_number: int, target_doc: CoverLetterDocument) -> CoverLetterDocument:
        v = self.get_version(cover_letter_id, version_number)
        if not v:
            raise CoverLetterNotFoundError(f"Version {version_number} of cover letter '{cover_letter_id}' not found.")

        snap = v.document_snapshot
        restored = CoverLetterDocument(**snap)
        # Restore into a fresh draft incrementing version
        restored.current_version = target_doc.current_version + 1
        restored.status = WritingDocumentStatus.DRAFT
        restored.updated_at = datetime.now(UTC)
        return restored
