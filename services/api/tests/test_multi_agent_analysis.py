"""Unit tests for multi-agent capabilities and agent integration (Section 121)."""

import pytest

from app.recruitment.intelligence.capabilities import (
    JOB_INTELLIGENCE_CAPABILITIES,
    capability_get_status,
)


@pytest.mark.asyncio
async def test_capabilities_registry_and_status():
    expected_capabilities = [
        "job.intelligence.analyze",
        "job.intelligence.analyze_batch",
        "job.intelligence.get_record",
        "job.intelligence.get_requirements",
        "job.intelligence.get_skills",
        "job.intelligence.get_education",
        "job.intelligence.get_experience",
        "job.intelligence.get_compensation",
        "job.intelligence.get_conditions",
        "job.intelligence.get_deadlines",
        "job.intelligence.get_evidence",
        "job.intelligence.get_conflicts",
        "job.intelligence.get_status",
    ]

    for cap in expected_capabilities:
        assert cap in JOB_INTELLIGENCE_CAPABILITIES
        assert callable(JOB_INTELLIGENCE_CAPABILITIES[cap])

    status_data = await capability_get_status()
    assert isinstance(status_data, dict)
    assert "total_records" in status_data
    assert "extractor_version" in status_data
    assert status_data["extractor_version"] == "1.0.0"
