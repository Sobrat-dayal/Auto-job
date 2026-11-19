"""Unit tests for Stage 25 Policy Pre-filtering in Discovery Engine (Stage 26)."""

import pytest
from app.recruitment.discovery.contracts import (
    ExtractedCompensation,
    ExtractedLocation,
    ExtractedPosting,
    PrefilterOutcome,
)
from app.recruitment.discovery.synchronization.coordinator import DiscoveryCoordinator


def test_prefilter_blocked_employer():
    coordinator = DiscoveryCoordinator()
    posting = ExtractedPosting(
        native_posting_id="p_blocked",
        title="Software Engineer",
        employer_name="Cyberdyne Systems",
        official_posting_url="https://example.com/jobs/1",
    )
    outcome, reasons = coordinator._evaluate_prefilter(posting, strategy_id="strat_backend_01")
    assert outcome in (PrefilterOutcome.PREFILTER_ACCEPTED, PrefilterOutcome.PREFILTER_REJECTED)


def test_prefilter_excluded_role():
    coordinator = DiscoveryCoordinator()
    posting = ExtractedPosting(
        native_posting_id="p_excl",
        title="Senior Engineering Manager",  # Defined as excluded in strat_backend_01
        employer_name="Stripe",
        official_posting_url="https://boards.greenhouse.io/stripe/jobs/100",
    )
    outcome, reasons = coordinator._evaluate_prefilter(posting, strategy_id="strat_backend_01")
    assert outcome == PrefilterOutcome.PREFILTER_REJECTED
    assert any("excluded title" in r.lower() for r in reasons)


def test_prefilter_salary_below_floor():
    coordinator = DiscoveryCoordinator()
    posting = ExtractedPosting(
        native_posting_id="p_low_sal",
        title="Backend Engineer",
        employer_name="Stripe",
        official_posting_url="https://boards.greenhouse.io/stripe/jobs/101",
        compensation=ExtractedCompensation(
            min_amount=50000.0,
            max_amount=60000.0,  # Below $90,000 floor in strat_backend_01
            currency="USD",
        ),
    )
    outcome, reasons = coordinator._evaluate_prefilter(posting, strategy_id="strat_backend_01")
    assert outcome == PrefilterOutcome.PREFILTER_REJECTED
    assert any("below floor" in r.lower() for r in reasons)


def test_prefilter_accepted_role():
    coordinator = DiscoveryCoordinator()
    posting = ExtractedPosting(
        native_posting_id="p_good",
        title="Backend Engineer",
        employer_name="Stripe",
        official_posting_url="https://boards.greenhouse.io/stripe/jobs/102",
        location=ExtractedLocation(is_remote=True, workplace_type="remote", country="United States"),
        compensation=ExtractedCompensation(
            min_amount=130000.0,
            max_amount=160000.0,
            currency="USD",
        ),
    )
    outcome, reasons = coordinator._evaluate_prefilter(posting, strategy_id="strat_backend_01")
    assert outcome == PrefilterOutcome.PREFILTER_ACCEPTED
