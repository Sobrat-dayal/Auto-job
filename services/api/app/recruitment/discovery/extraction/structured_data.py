"""Schema.org JobPosting structured data (JSON-LD) extraction (Stage 26)."""

import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger("autonom.recruitment.discovery.extraction.structured_data")

JSON_LD_REGEX = re.compile(
    r'<\s*script[^>]+type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</\s*script\s*>',
    re.IGNORECASE | re.DOTALL,
)


def extract_json_ld_job_postings(html_content: str) -> list[dict[str, Any]]:
    """Scan HTML for application/ld+json blocks matching schema.org JobPosting."""
    if not html_content:
        return []

    postings: list[dict[str, Any]] = []
    matches = JSON_LD_REGEX.findall(html_content)

    for match in matches:
        raw_json = match.strip()
        if not raw_json:
            continue
        try:
            data = json.loads(raw_json)
        except Exception:
            continue

        # Single object or graph
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue

            # Check @graph
            graph = item.get("@graph")
            if isinstance(graph, list):
                for node in graph:
                    if isinstance(node, dict) and _is_job_posting(node):
                        postings.append(node)

            if _is_job_posting(item):
                postings.append(item)

    return postings


def _is_job_posting(data: dict[str, Any]) -> bool:
    type_field = data.get("@type")
    if isinstance(type_field, str):
        return type_field.lower() == "jobposting"
    if isinstance(type_field, list):
        return any(str(t).lower() == "jobposting" for t in type_field)
    return False
