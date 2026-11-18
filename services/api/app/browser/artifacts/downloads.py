"""Download interception, validation, and tracking for browser automation."""

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from playwright.async_api import Download, Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.contracts import BrowserDownloadResponse, BrowserDownloadStatus
from app.core.config import settings
from app.db.models import BrowserDownloadRecord

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BrowserDownloadManager:
    """Manages file downloads from browser sessions with SHA-256 integrity checks."""

    def __init__(self, downloads_dir: Path | None = None) -> None:
        self.downloads_dir = downloads_dir or settings.browser_downloads_dir
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

    async def handle_download(
        self,
        db_session: AsyncSession,
        download: Download,
        session_id: str,
        tab_id: str | None = None,
    ) -> BrowserDownloadResponse:
        """Saves a Playwright download, computes its checksum, and logs a download record."""
        download_id = str(uuid4())
        suggested_name = download.suggested_filename
        # Sanitize filename
        safe_name = "".join(c for c in suggested_name if c.isalnum() or c in "._- ")
        if not safe_name:
            safe_name = f"download_{download_id[:8]}"

        dest_path = self.downloads_dir / f"{download_id[:8]}_{safe_name}"

        record = BrowserDownloadRecord(
            id=download_id,
            session_id=session_id,
            tab_id=tab_id,
            suggested_filename=suggested_name,
            destination_path=str(dest_path),
            file_size_bytes=0,
            sha256_checksum=None,
            mime_type=None,
            source_url=download.url,
            status=BrowserDownloadStatus.IN_PROGRESS.value,
            created_at=utc_now(),
            completed_at=None,
            error_message=None,
        )
        db_session.add(record)
        await db_session.commit()

        try:
            await download.save_as(str(dest_path))

            # Calculate SHA-256 and size
            file_bytes = dest_path.read_bytes()
            size = len(file_bytes)
            sha256 = hashlib.sha256(file_bytes).hexdigest()

            record.file_size_bytes = size
            record.sha256_checksum = sha256
            record.status = BrowserDownloadStatus.COMPLETED.value
            record.completed_at = utc_now()
            await db_session.commit()

            logger.info(f"Completed download {download_id} ({suggested_name}, {size} bytes, sha256={sha256[:12]}...)")

        except Exception as exc:
            logger.error(f"Failed download {download_id}: {exc}")
            record.status = BrowserDownloadStatus.FAILED.value
            record.error_message = str(exc)
            record.completed_at = utc_now()
            await db_session.commit()

        return self._to_response(record)

    async def list_downloads(self, db_session: AsyncSession) -> list[BrowserDownloadResponse]:
        """Lists recent downloads."""
        stmt = select(BrowserDownloadRecord).order_by(BrowserDownloadRecord.created_at.desc()).limit(100)
        res = await db_session.execute(stmt)
        records = res.scalars().all()
        return [self._to_response(r) for r in records]

    def _to_response(self, r: BrowserDownloadRecord) -> BrowserDownloadResponse:
        return BrowserDownloadResponse(
            id=r.id,
            session_id=r.session_id,
            tab_id=r.tab_id,
            suggested_filename=r.suggested_filename,
            destination_path=r.destination_path,
            file_size_bytes=r.file_size_bytes,
            sha256_checksum=r.sha256_checksum,
            mime_type=r.mime_type,
            source_url=r.source_url,
            status=BrowserDownloadStatus(r.status) if r.status in BrowserDownloadStatus._value2member_map_ else BrowserDownloadStatus.FAILED,
            created_at=r.created_at,
            completed_at=r.completed_at,
            error_message=r.error_message,
        )
