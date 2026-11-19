"""Unit tests for requirement logical relationships (Section 110)."""

import pytest

from app.recruitment.intelligence.contracts import LogicalOperator
from app.recruitment.intelligence.extraction.requirement_logic import detect_logical_operator


def test_logical_operator_and():
    op, count = detect_logical_operator("Proficiency in Python and SQL is required")
    assert op == LogicalOperator.AND
    assert count is None


def test_logical_operator_or():
    op, count = detect_logical_operator("Experience with either Python or Go")
    assert op == LogicalOperator.OR
    assert count is None


def test_logical_operator_at_least_n():
    op, count = detect_logical_operator("At least two of the following: Python, Java, Rust")
    assert op == LogicalOperator.AT_LEAST_N
    assert count == 2

    op2, count2 = detect_logical_operator("Any 3 of AWS, GCP, Azure, Kubernetes")
    assert op2 == LogicalOperator.AT_LEAST_N
    assert count2 == 3

    op3, count3 = detect_logical_operator("One or more of Python, C++, Go")
    assert op3 == LogicalOperator.AT_LEAST_N
    assert count3 == 1


def test_logical_operator_equivalent_alternative():
    op, count = detect_logical_operator("Bachelor's degree in Computer Science or equivalent practical experience")
    assert op == LogicalOperator.EQUIVALENT_ALTERNATIVE
    assert count is None
