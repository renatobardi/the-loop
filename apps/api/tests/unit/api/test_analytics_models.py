"""Unit tests for analytics API response models."""

from __future__ import annotations

from src.api.models.analytics import (
    CategoryStatsResponse,
    SummaryResponse,
    TeamStatsResponse,
    TimelinePointResponse,
)


def test_summary_response_all_fields() -> None:
    """SummaryResponse accepts all fields including nullable avg_resolution_days."""
    m = SummaryResponse(total=10, resolved=7, unresolved=3, avg_resolution_days=2.5)
    assert m.total == 10
    assert m.resolved == 7
    assert m.unresolved == 3
    assert m.avg_resolution_days == 2.5


def test_summary_response_null_avg() -> None:
    """avg_resolution_days defaults to None."""
    m = SummaryResponse(total=5, resolved=0, unresolved=5)
    assert m.avg_resolution_days is None


def test_summary_response_zero_counts() -> None:
    """Zero counts are valid (empty result set)."""
    m = SummaryResponse(total=0, resolved=0, unresolved=0)
    assert m.total == 0


def test_category_stats_response_fields() -> None:
    """CategoryStatsResponse holds all per-category stats."""
    m = CategoryStatsResponse(
        category="code_pattern",
        count=5,
        percentage=50.0,
        avg_severity=0.75,
        avg_resolution_days=3.2,
    )
    assert m.category == "code_pattern"
    assert m.percentage == 50.0
    assert m.avg_severity == 0.75
    assert m.avg_resolution_days == 3.2


def test_category_stats_response_null_resolution() -> None:
    """avg_resolution_days can be None for unresolved-only periods."""
    m = CategoryStatsResponse(
        category="unknown",
        count=2,
        percentage=20.0,
        avg_severity=0.5,
    )
    assert m.avg_resolution_days is None


def test_team_stats_response_fields() -> None:
    """TeamStatsResponse holds team name, count, top_categories, and optional resolution."""
    m = TeamStatsResponse(
        team="backend",
        count=8,
        top_categories=["code_pattern", "infrastructure"],
        avg_resolution_days=1.5,
    )
    assert m.team == "backend"
    assert m.count == 8
    assert m.top_categories == ["code_pattern", "infrastructure"]
    assert m.avg_resolution_days == 1.5


def test_team_stats_response_empty_categories() -> None:
    """top_categories can be an empty list."""
    m = TeamStatsResponse(team="ops", count=0, top_categories=[])
    assert m.top_categories == []
    assert m.avg_resolution_days is None


def test_timeline_point_response_fields() -> None:
    """TimelinePointResponse holds week ISO string, count, and by_category dict."""
    by_cat = {
        "code_pattern": 3,
        "infrastructure": 1,
        "process_breakdown": 0,
        "third_party": 0,
        "unknown": 0,
    }
    m = TimelinePointResponse(week="2026-01-05", count=4, by_category=by_cat)
    assert m.week == "2026-01-05"
    assert m.count == 4
    assert m.by_category["code_pattern"] == 3


def test_timeline_point_response_empty_categories() -> None:
    """by_category can be an empty dict (edge case)."""
    m = TimelinePointResponse(week="2026-01-05", count=0, by_category={})
    assert m.by_category == {}
