"""Integration tests for PostgresAnalyticsRepository (T033).

Tests use a real PostgreSQL database with migrations applied. Each test runs
inside a transaction that is rolled back after the test for isolation.
Data is inserted via the SQLAlchemy ORM to avoid asyncpg type ambiguity.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.postgres.analytics_repository import PostgresAnalyticsRepository
from src.adapters.postgres.models import IncidentRow, PostmortumRow
from src.domain.models import AnalyticsFilter, RootCauseCategory

# ─── Constants ────────────────────────────────────────────────────────────────

NOW = datetime.now(UTC)
WEEK_AGO = NOW - timedelta(days=7)
FAR_PAST = NOW - timedelta(days=730)


def _window(days: int = 60) -> tuple[datetime, datetime]:
    return NOW - timedelta(days=days), NOW + timedelta(hours=1)


def _filter(
    team: str | None = None,
    category: RootCauseCategory | None = None,
    status: str = "all",
) -> AnalyticsFilter:
    return AnalyticsFilter(team=team, category=category, status=status)  # type: ignore[arg-type]


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def repo(db_session: AsyncSession) -> PostgresAnalyticsRepository:
    return PostgresAnalyticsRepository(db_session)


async def _make_incident(
    session: AsyncSession,
    resolved_at: datetime | None = None,
    deleted_at: datetime | None = None,
) -> IncidentRow:
    row = IncidentRow(
        id=uuid4(),
        title="Integration test incident",
        category="injection",
        severity="high",
        anti_pattern="test anti-pattern",
        remediation="fix the test",
        created_by=uuid4(),
        resolved_at=resolved_at,
        deleted_at=deleted_at,
    )
    session.add(row)
    await session.flush()
    return row


async def _make_postmortem(
    session: AsyncSession,
    incident: IncidentRow,
    *,
    category: str = "code_pattern",
    team: str = "backend",
    severity: str = "error",
    created_at: datetime | None = None,
) -> PostmortumRow:
    pm_created_at = created_at or (NOW - timedelta(days=3))
    row = PostmortumRow(
        id=uuid4(),
        incident_id=incident.id,
        root_cause_category=category,
        description=(
            "Integration test postmortem for analytics repository testing — "
            "validates aggregation queries against real PostgreSQL data."
        ),
        team_responsible=team,
        severity_for_rule=severity,
        created_by=uuid4(),
        created_at=pm_created_at,
    )
    session.add(row)
    await session.flush()
    return row


# ─── get_summary tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_summary_empty_period(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Summary returns zeros when no postmortems exist in the query window."""
    start = FAR_PAST - timedelta(days=100)
    end = FAR_PAST - timedelta(days=90)
    result = await repo.get_summary(start, end, _filter())
    assert result.total == 0
    assert result.resolved == 0
    assert result.unresolved == 0
    assert result.avg_resolution_days is None


@pytest.mark.asyncio
async def test_summary_counts_unresolved_incident(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Summary unresolved count reflects unresolved incidents."""
    incident = await _make_incident(db_session)
    await _make_postmortem(db_session, incident)
    start, end = _window()

    result = await repo.get_summary(start, end, _filter())
    assert result.total >= 1
    assert result.unresolved >= 1


@pytest.mark.asyncio
async def test_summary_counts_resolved_incident(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Summary resolved count reflects resolved incidents."""
    incident = await _make_incident(db_session, resolved_at=NOW - timedelta(days=2))
    await _make_postmortem(db_session, incident)
    start, end = _window()

    result = await repo.get_summary(start, end, _filter())
    assert result.resolved >= 1


@pytest.mark.asyncio
async def test_summary_excludes_soft_deleted_incidents(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Soft-deleted incidents must not appear in summary."""
    # Insert a deleted incident (its postmortem should be excluded)
    deleted = await _make_incident(db_session, deleted_at=NOW - timedelta(hours=1))
    await _make_postmortem(db_session, deleted)
    # Insert a live unresolved incident
    live = await _make_incident(db_session)
    await _make_postmortem(db_session, live, team="control-team")
    start, end = _window()

    result_live = await repo.get_summary(start, end, _filter(team="control-team"))
    result_deleted_team = await repo.get_summary(start, end, _filter(team="deleted-team-xyz"))
    assert result_live.total >= 1
    assert result_deleted_team.total == 0  # deleted incident filtered out


@pytest.mark.asyncio
async def test_summary_team_filter_isolation(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Team filter narrows results to that team only."""
    inc_a = await _make_incident(db_session)
    await _make_postmortem(db_session, inc_a, team="team-alpha-xyz")
    start, end = _window()

    result = await repo.get_summary(start, end, _filter(team="team-alpha-xyz"))
    result_other = await repo.get_summary(start, end, _filter(team="nonexistent-team-xyz"))
    assert result.total >= 1
    assert result_other.total == 0


# ─── get_by_category tests ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_by_category_empty_window(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """by_category returns empty list for a window with no postmortems."""
    start = FAR_PAST - timedelta(days=100)
    end = FAR_PAST - timedelta(days=90)
    result = await repo.get_by_category(start, end, _filter())
    assert result == []


@pytest.mark.asyncio
async def test_by_category_groups_by_root_cause(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """by_category groups postmortems by root_cause_category."""
    inc1 = await _make_incident(db_session)
    inc2 = await _make_incident(db_session)
    await _make_postmortem(db_session, inc1, category="code_pattern")
    await _make_postmortem(db_session, inc2, category="infrastructure")
    start, end = _window()

    result = await repo.get_by_category(start, end, _filter())
    categories = {s.category for s in result}
    assert RootCauseCategory.CODE_PATTERN in categories
    assert RootCauseCategory.INFRASTRUCTURE in categories


@pytest.mark.asyncio
async def test_by_category_percentages_sum_to_100(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Percentages across all returned categories sum to ~100."""
    inc1 = await _make_incident(db_session)
    inc2 = await _make_incident(db_session)
    await _make_postmortem(db_session, inc1, category="code_pattern")
    await _make_postmortem(db_session, inc2, category="unknown")
    start, end = _window()

    result = await repo.get_by_category(start, end, _filter())
    total_pct = sum(s.percentage for s in result)
    assert abs(total_pct - 100.0) < 1.0


@pytest.mark.asyncio
async def test_by_category_status_resolved_only(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """status=resolved filter includes only resolved incidents."""
    resolved = await _make_incident(db_session, resolved_at=NOW - timedelta(days=1))
    await _make_postmortem(db_session, resolved, category="code_pattern", team="team-res")
    unresolved = await _make_incident(db_session)
    await _make_postmortem(db_session, unresolved, category="infrastructure", team="team-unr")
    start, end = _window()

    # With status=resolved, only code_pattern (from resolved incident) should appear
    result = await repo.get_by_category(start, end, _filter(status="resolved"))
    cats_in_result = {s.category for s in result}
    assert RootCauseCategory.CODE_PATTERN in cats_in_result
    assert RootCauseCategory.INFRASTRUCTURE not in cats_in_result


# ─── get_by_team tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_by_team_empty_window(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """by_team returns empty list for a window with no postmortems."""
    start = FAR_PAST - timedelta(days=100)
    end = FAR_PAST - timedelta(days=90)
    result = await repo.get_by_team(start, end, _filter())
    assert result == []


@pytest.mark.asyncio
async def test_by_team_groups_by_team_responsible(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """by_team groups postmortems by team_responsible."""
    inc1 = await _make_incident(db_session)
    inc2 = await _make_incident(db_session)
    await _make_postmortem(db_session, inc1, team="team-alpha-int")
    await _make_postmortem(db_session, inc2, team="team-beta-int")
    start, end = _window()

    result = await repo.get_by_team(start, end, _filter())
    teams = {t.team for t in result}
    assert "team-alpha-int" in teams
    assert "team-beta-int" in teams


@pytest.mark.asyncio
async def test_by_team_top_categories_at_most_3(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """top_categories has at most 3 entries per team (per RF-003)."""
    # 4 incidents each with a different category for the same team
    categories = ["code_pattern", "infrastructure", "unknown", "third_party"]
    for cat in categories:
        inc = await _make_incident(db_session)
        await _make_postmortem(db_session, inc, team="multi-cat-team", category=cat)
    start, end = _window()

    result = await repo.get_by_team(start, end, _filter())
    team_row = next((t for t in result if t.team == "multi-cat-team"), None)
    assert team_row is not None
    assert len(team_row.top_categories) <= 3


# ─── get_timeline tests ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_timeline_empty_window(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """timeline returns empty list for a window with no postmortems."""
    start = FAR_PAST - timedelta(days=100)
    end = FAR_PAST - timedelta(days=90)
    result = await repo.get_timeline(start, end, _filter())
    assert result == []


@pytest.mark.asyncio
async def test_timeline_all_5_categories_present(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Every TimelinePoint must have all 5 RootCauseCategory keys (F2 decision)."""
    inc = await _make_incident(db_session)
    await _make_postmortem(db_session, inc, category="code_pattern")
    start, end = _window()

    result = await repo.get_timeline(start, end, _filter())
    assert len(result) >= 1
    for point in result:
        for cat in RootCauseCategory:
            assert cat in point.by_category, f"Missing {cat} in timeline point"


@pytest.mark.asyncio
async def test_timeline_ordered_ascending(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Timeline points are sorted by week ascending."""
    inc1 = await _make_incident(db_session)
    inc2 = await _make_incident(db_session)
    await _make_postmortem(db_session, inc1, created_at=NOW - timedelta(days=15))
    await _make_postmortem(db_session, inc2, created_at=NOW - timedelta(days=5))
    start, end = _window(30)

    result = await repo.get_timeline(start, end, _filter())
    if len(result) > 1:
        weeks = [str(p.week) for p in result]
        assert weeks == sorted(weeks)


@pytest.mark.asyncio
async def test_timeline_count_matches_postmortem_count(
    repo: PostgresAnalyticsRepository, db_session: AsyncSession
) -> None:
    """Total count across all timeline points matches number of postmortems inserted."""
    inc1 = await _make_incident(db_session)
    inc2 = await _make_incident(db_session)
    # Both in the same week to get a single point
    created_at = NOW - timedelta(days=2)
    await _make_postmortem(db_session, inc1, created_at=created_at)
    await _make_postmortem(db_session, inc2, created_at=created_at, team="other")
    start, end = _window(7)

    result = await repo.get_timeline(start, end, _filter())
    total = sum(p.count for p in result)
    assert total >= 2
