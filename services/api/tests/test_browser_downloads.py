"""Tests for browser download management, SHA-256 integrity, and artifact storage."""

import hashlib
from uuid import uuid4
import pytest
from app.browser.artifacts.downloads import BrowserDownloadManager
from app.db.engine import get_db_session
from app.db.models import BrowserDownloadRecord


@pytest.mark.asyncio
async def test_download_manager_list_and_persistence(tmp_path):
    mgr = BrowserDownloadManager(downloads_dir=tmp_path)
    dl_id = f"dl_test_{uuid4().hex[:8]}"

    # Create dummy download file
    sample_content = b"AUTONOM Job Description PDF Mock Content"
    checksum = hashlib.sha256(sample_content).hexdigest()
    dest_file = tmp_path / "job_desc.pdf"
    dest_file.write_bytes(sample_content)

    async with get_db_session() as db:
        record = BrowserDownloadRecord(
            id=dl_id,
            session_id="sess_mock_1",
            tab_id=None,
            suggested_filename="job_desc.pdf",
            destination_path=str(dest_file),
            file_size_bytes=len(sample_content),
            sha256_checksum=checksum,
            mime_type="application/pdf",
            source_url="https://example.com/job_desc.pdf",
            status="completed",
        )
        db.add(record)
        await db.commit()

        # List downloads
        downloads = await mgr.list_downloads(db)
        assert len(downloads) >= 1
        found = next((d for d in downloads if d.id == dl_id), None)
        assert found is not None
        assert found.suggested_filename == "job_desc.pdf"
        assert found.sha256_checksum == checksum
        assert found.file_size_bytes == len(sample_content)
        assert found.status.value == "completed"
