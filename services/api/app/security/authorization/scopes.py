"""Resource scope validation, canonical path resolution, and URL boundary checks."""

import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger("autonom.security.authorization.scopes")


def is_safe_filesystem_path(target_path_str: str, allowed_root_str: str) -> bool:
    """Verifies that target_path resolves strictly within allowed_root, preventing traversal and symlink escapes."""
    try:
        target = Path(target_path_str).resolve()
        allowed_root = Path(allowed_root_str).resolve()

        # Check if target is equal to or relative to allowed_root
        target.relative_to(allowed_root)
        return True
    except (ValueError, RuntimeError) as e:
        logger.warning(
            "Filesystem path traversal or scope violation: '%s' is outside root '%s': %s",
            target_path_str,
            allowed_root_str,
            e,
        )
        return False


def is_safe_network_url(target_url_str: str, allowed_origins: list[str]) -> bool:
    """Validates that target_url strictly matches one of the allowed origins without substring confusion.

    E.g. If allowed origin is 'https://indeed.com', 'https://attacker-indeed.com' is REJECTED.
    """
    try:
        parsed_target = urlparse(target_url_str)
        target_scheme = parsed_target.scheme.lower()
        target_host = (parsed_target.hostname or "").lower()

        if target_scheme not in ("http", "https"):
            return False

        for origin in allowed_origins:
            if origin == "*":
                return True

            parsed_origin = urlparse(origin)
            origin_scheme = parsed_origin.scheme.lower()
            origin_host = (parsed_origin.hostname or "").lower()

            if origin_scheme and origin_scheme != target_scheme:
                continue

            if not origin_host:
                # Might have been specified bare e.g. "indeed.com"
                origin_host = origin.lower().split("/")[0]

            if origin_host.startswith("*."):
                suffix = origin_host[2:]
                if target_host == suffix or target_host.endswith("." + suffix):
                    return True
            elif target_host == origin_host:
                # Also check path prefix if origin has a path
                origin_path = parsed_origin.path.rstrip("/")
                if origin_path and not parsed_target.path.startswith(origin_path):
                    continue
                return True

        return False
    except Exception as e:
        logger.warning("URL parsing error during scope check: %s", e)
        return False


def matches_resource_scope(
    requested_scope: dict[str, Any],
    policy_scope: dict[str, Any],
) -> bool:
    """Evaluates whether a requested resource scope is fully enclosed within an allowed policy scope."""
    if not policy_scope or policy_scope.get("unrestricted") is True:
        return True

    # 1. Filesystem check
    if "allowed_paths" in policy_scope and "path" in requested_scope:
        req_path = requested_scope["path"]
        allowed_paths = policy_scope["allowed_paths"]
        if isinstance(allowed_paths, str):
            allowed_paths = [allowed_paths]

        path_ok = any(is_safe_filesystem_path(req_path, root) for root in allowed_paths)
        if not path_ok:
            return False

    # 2. Network URL check
    if "allowed_origins" in policy_scope and "url" in requested_scope:
        req_url = requested_scope["url"]
        allowed_origins = policy_scope["allowed_origins"]
        if isinstance(allowed_origins, str):
            allowed_origins = [allowed_origins]

        url_ok = is_safe_network_url(req_url, allowed_origins)
        if not url_ok:
            return False

    # 3. Recruitment job source check
    if "allowed_sources" in policy_scope and "source" in requested_scope:
        req_src = str(requested_scope["source"]).lower()
        allowed_srcs = [str(s).lower() for s in policy_scope["allowed_sources"]]
        if "*" not in allowed_srcs and req_src not in allowed_srcs:
            return False

    # 4. Recruitment excluded company check
    if "excluded_companies" in policy_scope and "company" in requested_scope:
        req_comp = str(requested_scope["company"]).lower()
        excluded = [str(c).lower() for c in policy_scope["excluded_companies"]]
        if any(ex in req_comp for ex in excluded):
            logger.warning("Company '%s' is explicitly excluded by recruitment policy", req_comp)
            return False

    # 5. Recruitment minimum match score check
    if "min_match_score" in policy_scope and "match_score" in requested_scope:
        try:
            req_score = float(requested_scope["match_score"])
            min_score = float(policy_scope["min_match_score"])
            if req_score < min_score:
                logger.info("Match score %s is below required threshold %s", req_score, min_score)
                return False
        except (ValueError, TypeError):
            return False

    return True
