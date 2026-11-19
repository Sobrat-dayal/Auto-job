"""Unit tests for description versioning and reanalysis triggers (Section 122)."""

import pytest

from app.recruitment.intelligence.lifecycle.versions import (
    compute_description_hash,
    is_reanalysis_needed,
)


def test_description_hashing_and_reanalysis_triggers():
    desc_v1 = "Software Engineer. Minimum 3 years Python."
    desc_v2 = "Senior Software Engineer. Minimum 5 years Python and AWS."

    hash_v1 = compute_description_hash(desc_v1)
    hash_v2 = compute_description_hash(desc_v2)

    assert hash_v1 != hash_v2
    assert len(hash_v1) == 64  # SHA-256

    # Reanalysis is NOT needed if description is identical
    assert is_reanalysis_needed(hash_v1, desc_v1) is False

    # Reanalysis IS needed if description has changed
    assert is_reanalysis_needed(hash_v1, desc_v2) is True
