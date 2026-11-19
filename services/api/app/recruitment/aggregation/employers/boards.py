"""Employer ATS Board Token Extraction & Mapping (Stage 27)."""

import re
from urllib.parse import urlparse
from typing import Optional


def extract_ats_board_token(url: str, provider: Optional[str] = None) -> Optional[tuple[str, str]]:
    """Extract (provider, board_token) from a job posting or careers URL.

    Examples:
      https://boards.greenhouse.io/stripe/jobs/123 -> ('greenhouse', 'stripe')
      https://jobs.lever.co/netflix/456 -> ('lever', 'netflix')
      https://jobs.ashbyhq.com/openai/789 -> ('ashby', 'openai')
    """
    if not url:
        return None

    try:
        parsed = urlparse(url.strip())
        netloc = parsed.netloc.lower()
        path = parsed.path.strip("/")
        parts = path.split("/")

        if "greenhouse.io" in netloc and parts:
            # Often boards.greenhouse.io/<board_token>
            token = parts[0]
            if token.lower() in {"embed", "jobs", "v1"}:
                token = parts[1] if len(parts) > 1 else token
            return "greenhouse", token.lower()

        if "lever.co" in netloc and parts:
            # jobs.lever.co/<board_token>
            return "lever", parts[0].lower()

        if "ashbyhq.com" in netloc and parts:
            # jobs.ashbyhq.com/<board_token>
            return "ashby", parts[0].lower()

        if provider and parts:
            return provider.lower(), parts[0].lower()

        return None
    except Exception:
        return None
