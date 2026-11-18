"""State Fingerprint extraction and hashing for persistent checkpoints."""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, Optional

from app.computer.workflow_reliability.contracts import StateFingerprint


class StateFingerprintService:
    """Captures bounded, non-sensitive application and environment fingerprints."""

    @staticmethod
    def capture_fingerprint(
        browser_info: Optional[Dict[str, Any]] = None,
        native_info: Optional[Dict[str, Any]] = None,
        visual_info: Optional[Dict[str, Any]] = None,
        artifact_info: Optional[Dict[str, Any]] = None,
        window_title: Optional[str] = None,
        process_name: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs: Any,
    ) -> StateFingerprint:
        """Create a privacy-conscious StateFingerprint."""
        n_info = dict(native_info or {})
        if window_title:
            n_info["window_title"] = window_title
        if process_name:
            n_info["process_name"] = process_name

        b_info = dict(browser_info or {})
        if url:
            b_info["url"] = url
            b_info["origin"] = url

        clean_browser = None
        if b_info:
            clean_browser = {
                "origin": b_info.get("origin") or b_info.get("url", "").split("?")[0],
                "title": b_info.get("title", ""),
                "tab_count": b_info.get("tab_count", 1),
            }

        clean_native = None
        if n_info:
            clean_native = {
                "process_name": n_info.get("process_name", ""),
                "window_title": n_info.get("window_title", ""),
                "is_foreground": n_info.get("is_foreground", True),
            }

        clean_visual = None
        if visual_info:
            clean_visual = {
                "display_index": visual_info.get("display_index", 0),
                "resolution": visual_info.get("resolution", "1920x1080"),
                "frame_hash": visual_info.get("frame_hash", "")[:16],
            }

        clean_artifact = None
        if artifact_info:
            clean_artifact = {
                "file_path": artifact_info.get("file_path", ""),
                "file_hash": artifact_info.get("file_hash", ""),
                "file_size": artifact_info.get("file_size", 0),
            }

        return StateFingerprint(
            browser_state=clean_browser,
            native_state=clean_native,
            visual_state=clean_visual,
            artifact_state=clean_artifact,
            captured_at=datetime.now(timezone.utc),
        )
