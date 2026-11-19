"""Deterministic Schema.org JobPosting JSON-LD extractor."""

import json
import re
from typing import Any


def extract_schema_org_jobposting(raw_html: str) -> dict[str, Any] | None:
    """Extract Schema.org JobPosting JSON-LD from HTML markup if present."""
    if not raw_html or ("application/ld+json" not in raw_html and "JobPosting" not in raw_html):
        return None

    # Search for ld+json scripts
    pattern = re.compile(
        r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>([\s\S]*?)</script>',
        re.IGNORECASE,
    )

    matches = pattern.findall(raw_html)
    for block in matches:
        try:
            data = json.loads(block.strip())
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        return item
            elif isinstance(data, dict):
                if data.get("@type") == "JobPosting":
                    return data
                if "@graph" in data and isinstance(data["@graph"], list):
                    for item in data["@graph"]:
                        if isinstance(item, dict) and item.get("@type") == "JobPosting":
                            return item
        except Exception:
            continue

    return None
