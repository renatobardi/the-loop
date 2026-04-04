"""Unit tests for AnalyticsService — period parsing, normalization, delegation."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.domain.models import (
    AnalyticsFilter,
    AnalyticsPeriod,
    AnalyticsSummary,
    CategoryStats,
    RootCauseCategory,
    TeamStats,
    TimelinePoint,
)
from src.domain.services import AnalyticsService


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(mock_repo: MagicMock) -> AnalyticsService:
    return AnalyticsService(mock_repo)


def _default_filter() -> AnalyticsFilter:
    return AnalyticsFilter(team=None, category=None, status="all")


def _make_summary() -> AnalyticsSummary:
    return AnalyticsSummary(total=5, resolved=3, unresolved=2, avg_resolution_days=1.5)


def _make_category_stats(pct_a: float = 60.0, pct_b: float = 40.0) -> list[CategoryStats]:
    return [
        CategoryStats(
            category=RootCauseCategory.CODE_PATTERN,
            count=6,
            percentage=pct_a,
            avg_severity=1.0,
        ),
        CategoryStats(
            category=RootCauseCategory.INFRASTRUCTURE,
            count=4,
            percentage=pct_b,
            avg_severity=0.5,
        ),
    ]


# ─── _parse_period ──────────────────────��─────────────────────────────────────


def test_parse_period_week(service: AnalyticsService) -> None:
    """Period=week should span last 7 days."""
    period = AnalyticsPeriod(value="week")
    start, end = service._parse_period(period)
    delta = end - start
    assert 6 <= delta.days <= 7


def test_parse_period_month(service: AnalyticsService) -> None:
    """Period=month should span last 30 days."""
    period = AnalyticsPeriod(value="month")
    start, end = service._parse_period(period)
    delta = end - start
    assert 29 <= delta.days <= 30


def test_parse_period_quarter(service: AnalyticsService) -> None:
    """Period=quarter should start at the beginning of the current calendar quarter."""
    period = AnalyticsPeriod(value="quarter")
    start, end = service._parse_period(period)
    # Start should be on day 1 of a quarter-start month (1, 4, 7, 10)
    assert start.day == 1
    assert start.month in {1, 4, 7, 10}
    assert end >= start


def test_parse_period_custom(service: AnalyticsService) -> None:
    """Period=custom should use provided start/end dates."""
    sd = datetime(2025, 1, 1, tzinfo=UTC)
    ed = datetime(2025, 3, 31, tzinfo=UTC)
    period = AnalyticsPeriod(value="custom", start_date=sd, end_date=ed)
    start, end = service._parse_period(period)
    assert start.year == 2025 and start.month == 1 and start.day == 1
    assert end.year == 2025 and end.month == 3 and end.day == 31


# ─── _normalize_stats ─────────────────────────────────────────────────────────


def test_normalize_stats_exact_sum(service: AnalyticsService) -> None:
    """Percentages already summing to 100 should not be changed."""
    stats = _make_category_stats(60.0, 40.0)
    result = service._normalize_stats(stats)
    total = sum(s.percentage for s in result)
    assert abs(total - 100.0) < 0.01


def test_normalize_stats_drift_correction(service: AnalyticsService) -> None:
    """Percentages drifting from 100 should be renormalized."""
    stats = _make_category_stats(60.1, 40.1)  # sum = 100.2
    result = service._normalize_stats(stats)
    total = sum(s.percentage for s in result)
    assert abs(total - 100.0) < 0.1


def test_normalize_stats_empty(service: AnalyticsService) -> None:
    """Empty list should return empty list."""
    assert service._normalize_stats([]) == []


def test_normalize_stats_zero_percentage(service: AnalyticsService) -> None:
    """All-zero percentages should return stats unchanged."""
    stats = _make_category_stats(0.0, 0.0)
    result = service._normalize_stats(stats)
    assert result == stats


# ─── Service delegation ───────────────────────────────────────────────────────


async def test_get_summary_delegates_to_repo(
    service: AnalyticsService, mock_repo: MagicMock
) -> None:
    """get_summary() should call repo.get_summary with parsed dates."""
    expected = _make_summary()
    mock_repo.get_summary = AsyncMock(return_value=expected)

    period = AnalyticsPeriod(value="month")
    filters = _default_filter()
    result = await service.get_summary(period, filters)

    assert result == expected
    mock_repo.get_summary.assert_called_once()
    args = mock_repo.get_summary.call_args[0]
    start, end, f = args
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert f == filters


async def test_get_by_category_delegates_and_normalizes(
    service: AnalyticsService, mock_repo: MagicMock
) -> None:
    """get_by_category() should normalize percentages."""
    stats = _make_category_stats(60.1, 40.1)
    mock_repo.get_by_category = AsyncMock(return_value=stats)

    result = await service.get_by_category(AnalyticsPeriod(value="month"), _default_filter())

    assert len(result) == 2
    total = sum(s.percentage for s in result)
    assert abs(total - 100.0) < 0.1


async def test_get_by_team_delegates(
    service: AnalyticsService, mock_repo: MagicMock
) -> None:
    """get_by_team() should call repo and return results unchanged."""
    expected = [
        TeamStats(
            team="backend", count=3, top_categories=[RootCauseCategory.CODE_PATTERN],
            avg_resolution_days=2.0
        )
    ]
    mock_repo.get_by_team = AsyncMock(return_value=expected)

    result = await service.get_by_team(AnalyticsPeriod(value="week"), _default_filter())
    assert result == expected


async def test_get_timeline_delegates(
    service: AnalyticsService, mock_repo: MagicMock
) -> None:
    """get_timeline() should call repo and return timeline points."""
    expected = [
        TimelinePoint(
            week=datetime(2025, 1, 6, tzinfo=UTC),
            count=3,
            by_category={cat: 0 for cat in RootCauseCategory},
        )
    ]
    mock_repo.get_timeline = AsyncMock(return_value=expected)

    result = await service.get_timeline(AnalyticsPeriod(value="month"), _default_filter())
    assert result == expected
    assert len(result) == 1
