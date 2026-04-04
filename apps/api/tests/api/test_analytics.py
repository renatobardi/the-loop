"""API-level tests for analytics routes — service mocked."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_analytics_service
from src.domain.models import (
    AnalyticsSummary,
    CategoryStats,
    RootCauseCategory,
    TeamStats,
    TimelinePoint,
)
from src.main import app

_USER = UUID("00000000-0000-0000-0000-000000000001")
_BASE = "/api/v1/incidents/analytics"


def _make_summary(**kwargs: object) -> AnalyticsSummary:
    defaults: dict[str, object] = {
        "total": 10,
        "resolved": 7,
        "unresolved": 3,
        "avg_resolution_days": 2.5,
    }
    defaults.update(kwargs)
    return AnalyticsSummary(**defaults)  # type: ignore[arg-type]


def _make_category_stats() -> list[CategoryStats]:
    return [
        CategoryStats(
            category=RootCauseCategory.CODE_PATTERN,
            count=5,
            percentage=50.0,
            avg_severity=1.0,
            avg_resolution_days=1.5,
        ),
        CategoryStats(
            category=RootCauseCategory.INFRASTRUCTURE,
            count=3,
            percentage=30.0,
            avg_severity=0.5,
            avg_resolution_days=3.0,
        ),
    ]


def _make_team_stats() -> list[TeamStats]:
    return [
        TeamStats(
            team="backend",
            count=6,
            top_categories=[RootCauseCategory.CODE_PATTERN, RootCauseCategory.INFRASTRUCTURE],
            avg_resolution_days=2.0,
        ),
        TeamStats(
            team="infra",
            count=4,
            top_categories=[RootCauseCategory.INFRASTRUCTURE],
            avg_resolution_days=None,
        ),
    ]


def _make_timeline() -> list[TimelinePoint]:
    from datetime import UTC, datetime

    return [
        TimelinePoint(
            week=datetime(2025, 1, 6, tzinfo=UTC),
            count=3,
            by_category={
                cat: (1 if cat == RootCauseCategory.CODE_PATTERN else 0)
                for cat in RootCauseCategory
            },
        ),
        TimelinePoint(
            week=datetime(2025, 1, 13, tzinfo=UTC),
            count=5,
            by_category={
                cat: (2 if cat == RootCauseCategory.INFRASTRUCTURE else 0)
                for cat in RootCauseCategory
            },
        ),
    ]


@pytest.fixture
def mock_analytics_service() -> AsyncMock:
    return AsyncMock()


async def test_get_summary_ok(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary returns 200 + valid JSON."""
    mock_analytics_service.get_summary = AsyncMock(return_value=_make_summary())

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/summary")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert data["resolved"] == 7
    assert data["unresolved"] == 3
    assert data["avg_resolution_days"] == 2.5


async def test_get_summary_null_avg(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary returns null avg_resolution_days when all unresolved."""
    mock_analytics_service.get_summary = AsyncMock(
        return_value=_make_summary(total=3, resolved=0, unresolved=3, avg_resolution_days=None)
    )

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/summary?status=unresolved")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["avg_resolution_days"] is None


async def test_get_summary_missing_auth() -> None:
    """GET /analytics/summary returns 401 or 403 when not authenticated."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/summary")
    app.dependency_overrides.clear()

    assert response.status_code in {401, 403}


async def test_get_by_category_ok(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/by-category returns stats per root cause category."""
    mock_analytics_service.get_by_category = AsyncMock(return_value=_make_category_stats())

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/by-category?team=backend")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["category"] == "code_pattern"
    assert data[0]["count"] == 5
    assert data[0]["percentage"] == 50.0


async def test_get_by_team_ok(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/by-team returns stats per team."""
    mock_analytics_service.get_by_team = AsyncMock(return_value=_make_team_stats())

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/by-team?category=infrastructure")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["team"] == "backend"
    assert data[0]["count"] == 6
    assert "code_pattern" in data[0]["top_categories"]


async def test_get_timeline_ok(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/timeline returns weekly points with by_category breakdown."""
    mock_analytics_service.get_timeline = AsyncMock(return_value=_make_timeline())

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/timeline?period=month")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "week" in data[0]
    assert "by_category" in data[0]
    assert "code_pattern" in data[0]["by_category"]


async def test_invalid_period_returns_400(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary with invalid period → 400."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/summary?period=invalid")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "period" in response.json()["detail"].lower()


async def test_custom_period_missing_dates_returns_400(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary with period=custom but missing dates → 400."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/summary?period=custom&start_date=2025-01-01")
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "end_date" in response.json()["detail"].lower()


async def test_invalid_status_returns_400(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary with invalid status → 400."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/summary?status=badstatus")
    app.dependency_overrides.clear()

    assert response.status_code == 400


async def test_invalid_category_returns_400(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/by-category with unknown category → 400."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/by-category?category=not_a_category")
    app.dependency_overrides.clear()

    assert response.status_code == 400


async def test_empty_results_returns_200(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/by-category with no data → 200 with empty list."""
    mock_analytics_service.get_by_category = AsyncMock(return_value=[])

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"{_BASE}/by-category")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []


async def test_custom_date_range_ok(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary with period=custom and valid date range → 200."""
    mock_analytics_service.get_summary = AsyncMock(return_value=_make_summary())

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            f"{_BASE}/summary?period=custom&start_date=2025-01-01&end_date=2025-01-31"
        )
    app.dependency_overrides.clear()

    assert response.status_code == 200


async def test_start_after_end_returns_400(mock_analytics_service: AsyncMock) -> None:
    """GET /analytics/summary with start_date > end_date → 400."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            f"{_BASE}/summary?period=custom&start_date=2025-02-01&end_date=2025-01-01"
        )
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "start_date" in response.json()["detail"].lower()
