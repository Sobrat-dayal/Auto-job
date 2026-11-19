"""Source Authority and Reliability Scoring Engine (Stage 27)."""

# Authority weights for different source origins (0.0 to 1.0)
SOURCE_AUTHORITY_SCORES = {
    "career_page": 0.95,
    "employer_career_site": 0.95,
    "official_public_api": 0.90,
    "greenhouse": 0.88,
    "lever": 0.88,
    "ashby": 0.88,
    "employer_ats_board": 0.85,
    "usajobs": 0.95,
    "json_feed": 0.70,
    "rss_atom": 0.65,
    "rss_atom_feed": 0.65,
    "url_import": 0.60,
    "manual_import": 0.50,
}


def get_source_authority_score(provider_or_category: str) -> float:
    """Return field authority score for a given source provider or category."""
    clean = provider_or_category.lower().strip()
    return SOURCE_AUTHORITY_SCORES.get(clean, 0.60)
