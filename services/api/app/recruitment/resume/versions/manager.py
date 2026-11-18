"""Resume Versioning, Approval Workflow & Comparison Engine (Stage 23)."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4
from app.recruitment.resume.contracts import (
    DocumentStatus,
    ResumeDocument,
    ResumeVersionRecord,
)
from app.recruitment.resume.errors import ResumeVersionNotFoundError

logger = logging.getLogger("autonom.recruitment.resume.versions.manager")


class ResumeVersionManager:
    """Maintains immutable historical versions of approved resumes and computes detailed diffs."""

    def __init__(self) -> None:
        self._versions: dict[str, list[ResumeVersionRecord]] = {}

    def list_versions(self, resume_id: str) -> list[ResumeVersionRecord]:
        return self._versions.get(resume_id, [])

    def get_version(self, resume_id: str, version_id: str) -> ResumeVersionRecord:
        vers = self.list_versions(resume_id)
        for v in vers:
            if v.id == version_id or str(v.version_number) == version_id:
                return v
        raise ResumeVersionNotFoundError(f"Version '{version_id}' not found for resume '{resume_id}'.")

    def create_version_snapshot(
        self,
        doc: ResumeDocument,
        actor_id: str = "user",
        changelog: str = "",
        is_published: bool = False,
    ) -> ResumeVersionRecord:
        dump = doc.model_dump(mode="json")
        content_bytes = json.dumps(dump, sort_keys=True).encode("utf-8")
        chash = hashlib.sha256(content_bytes).hexdigest()

        existing = self.list_versions(doc.id)
        next_ver_num = len(existing) + 1

        rec = ResumeVersionRecord(
            resume_id=doc.id,
            version_number=next_ver_num,
            profile_snapshot_id=doc.profile_snapshot_id,
            job_ref=doc.job_ref,
            template_id=doc.template_id,
            template_version=doc.template_version,
            content_hash=chash,
            changelog=changelog or f"Version {next_ver_num} created",
            actor_id=actor_id,
            is_published=is_published,
            document_snapshot=dump,
        )

        self._versions.setdefault(doc.id, []).append(rec)
        doc.current_version = next_ver_num
        logger.info(f"Recorded immutable resume version v{next_ver_num} ({rec.id}) for resume '{doc.id}'.")
        return rec

    @classmethod
    def compare_versions(
        cls,
        ver_a: ResumeVersionRecord,
        ver_b: ResumeVersionRecord,
    ) -> dict[str, Any]:
        """Calculates structural and textual differences between two historical resume versions."""
        snap_a = ver_a.document_snapshot
        snap_b = ver_b.document_snapshot

        diff: dict[str, Any] = {
            "version_a": ver_a.version_number,
            "version_b": ver_b.version_number,
            "template_changed": snap_a.get("template_id") != snap_b.get("template_id"),
            "target_role_changed": snap_a.get("target_role") != snap_b.get("target_role"),
            "section_order_changed": False,
            "sections_added": [],
            "sections_removed": [],
            "bullet_changes": [],
        }

        secs_a = {s["section_type"]: s for s in snap_a.get("sections", [])}
        secs_b = {s["section_type"]: s for s in snap_b.get("sections", [])}

        types_a = [s["section_type"] for s in snap_a.get("sections", [])]
        types_b = [s["section_type"] for s in snap_b.get("sections", [])]
        diff["section_order_changed"] = types_a != types_b

        diff["sections_added"] = [t for t in types_b if t not in secs_a]
        diff["sections_removed"] = [t for t in types_a if t not in secs_b]

        return diff
