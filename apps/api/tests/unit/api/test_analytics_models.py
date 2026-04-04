"""Unit tests for analytics API request/response models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.api.models.analytics import AnalyticsFilterRequest


def test_valid_period_accepted() -> None:
    """All valid period values should be accepted."""
    for period in ("week", "month", "quarter", "custom"):
        m = AnalyticsFilterRequest(period=period)
        assert m.period == period


def test_invalid_period_raises() -> None:
    """Invalid period should raise ValidationError."""
    with pytest.raises(ValidationError):
        AnalyticsFilterRequest(period="yearly")


def test_valid_status_accepted() -> None:
    """All valid status values should be accepted."""
    for status in ("resolved", "unresolved", "all"):
        m = AnalyticsFilterRequest(status=status)
        assert m.status == status


def test_invalid_status_raises() -> None:
    """Invalid status should raise ValidationError."""
    with pytest.raises(ValidationError):
        AnalyticsFilterRequest(status="pending")


def test_defaults() -> None:
    """Default period=month and status=all."""
    m = AnalyticsFilterRequest()
    assert m.period == "month"
    assert m.status == "all"
    assert m.team is None
    assert m.category is None
