"""Source authority ranking and hierarchy for reconciliation."""

# Higher number indicates higher authority
SOURCE_AUTHORITY_RANK: dict[str, int] = {
    "employer_portal": 100,
    "greenhouse": 90,
    "lever": 90,
    "ashby": 90,
    "usajobs": 95,
    "json_feed": 70,
    "rss_feed": 60,
    "job_board": 50,
    "manual_import": 40,
    "unknown": 10,
}


def get_source_authority(source_type: str) -> int:
    """Return numeric authority rank for a source provider."""
    return SOURCE_AUTHORITY_RANK.get(source_type.lower(), 10)
