"""PostgreSQL implementation of the AnalyticsRepoPort."""

from __future__ import annotations

import time
from datetime import datetime
from typing import cast

import structlog
from sqlalchemy import String, bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import TextClause

from src.adapters.postgres.analytics_queries import (
    QUERY_BY_CATEGORY,
    QUERY_BY_TEAM,
    QUERY_SUMMARY,
    QUERY_TIMELINE,
)
from src.domain.models import (
    AnalyticsFilter,
    AnalyticsSummary,
    CategoryStats,
    RootCauseCategory,
    TeamStats,
    TimelinePoint,
)

logger = structlog.get_logger(__name__)

# All 5 RootCauseCategory values — used to fill missing keys in by_category (F2 decision)
_ALL_CATEGORIES = list(RootCauseCategory)


def _build_params(
    start: datetime, end: datetime, filters: AnalyticsFilter
) -> dict[str, object]:
    """Build shared parameter dict for all analytics queries."""
    return {
        "start": start,
        "end": end,
        "team": filters.team,
        "category": filters.category.value if filters.category else None,
        "status": filters.status,
    }


def _typed_text(sql: str) -> TextClause:
    """Wrap a SQL string with explicit String types for nullable 'team' and 'category'.

    asyncpg cannot infer the PostgreSQL type of a Python None value in a named
    parameter (e.g. ':team IS NULL'). Adding String() type hints lets SQLAlchemy
    emit the correct type annotation so asyncpg knows these are TEXT columns.
    """
    return text(sql).bindparams(
        bindparam("team", type_=String()),
        bindparam("category", type_=String()),
    )


def _to_avg_days(raw: object) -> float | None:
    """Convert raw SQL avg_resolution_days to float | None."""
    return float(raw) if raw is not None else None  # type: ignore[arg-type]


class PostgresAnalyticsRepository:
    """Raw SQL analytics aggregations over postmortems + incidents."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> AnalyticsSummary:
        t0 = time.monotonic()
        params = _build_params(start, end, filters)
        result = await self._session.execute(_typed_text(QUERY_SUMMARY), params)
        row = result.mappings().one()
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.info(
            "analytics.query",
            query="summary",
            elapsed_ms=round(elapsed_ms, 1),
            result_count=1,
            period_start=start.isoformat(),
            period_end=end.isoformat(),
            team=filters.team,
            category=filters.category,
            status=filters.status,
        )
        return AnalyticsSummary(
            total=int(row["total"]),
            resolved=int(row["resolved"]),
            unresolved=int(row["unresolved"]),
            avg_resolution_days=_to_avg_days(row["avg_resolution_days"]),
        )

    async def get_by_category(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> list[CategoryStats]:
        t0 = time.monotonic()
        params = _build_params(start, end, filters)
        result = await self._session.execute(_typed_text(QUERY_BY_CATEGORY), params)
        rows = result.mappings().all()
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.info(
            "analytics.query",
            query="by_category",
            elapsed_ms=round(elapsed_ms, 1),
            result_count=len(rows),
            period_start=start.isoformat(),
            period_end=end.isoformat(),
            team=filters.team,
            category=filters.category,
            status=filters.status,
        )
        return [
            CategoryStats(
                category=RootCauseCategory(row["root_cause_category"]),
                count=int(row["count"]),
                percentage=float(row["percentage"] or 0),
                avg_severity=float(row["avg_severity"]),
                avg_resolution_days=_to_avg_days(row["avg_resolution_days"]),
            )
            for row in rows
        ]

    async def get_by_team(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> list[TeamStats]:
        t0 = time.monotonic()
        params = _build_params(start, end, filters)
        result = await self._session.execute(_typed_text(QUERY_BY_TEAM), params)
        rows = result.mappings().all()
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.info(
            "analytics.query",
            query="by_team",
            elapsed_ms=round(elapsed_ms, 1),
            result_count=len(rows),
            period_start=start.isoformat(),
            period_end=end.isoformat(),
            team=filters.team,
            category=filters.category,
            status=filters.status,
        )
        stats = []
        for row in rows:
            # Extract top 3 categories by count from the jsonb aggregation
            cat_counts: dict[str, int] = row["category_counts"] or {}
            top_categories = [
                RootCauseCategory(cat)
                for cat, _ in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            ]
            stats.append(
                TeamStats(
                    team=row["team"],
                    count=int(row["count"]),
                    top_categories=top_categories,
                    avg_resolution_days=_to_avg_days(row["avg_resolution_days"]),
                )
            )
        return stats

    async def get_timeline(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> list[TimelinePoint]:
        t0 = time.monotonic()
        params = _build_params(start, end, filters)
        result = await self._session.execute(text(QUERY_TIMELINE), params)
        rows = result.mappings().all()
        elapsed_ms = (time.monotonic() - t0) * 1000
        logger.info(
            "analytics.query",
            query="timeline",
            elapsed_ms=round(elapsed_ms, 1),
            result_count=len(rows),
            period_start=start.isoformat(),
            period_end=end.isoformat(),
            status=filters.status,
        )
        points = []
        for row in rows:
            # Always include all 5 categories (F2 decision) — fill missing with 0
            raw: dict[str, int] = row["by_category"] or {}
            # Build complete dict with all 5 categories (F2 decision); cast for mypy StrEnum
            by_category = cast(
                dict[RootCauseCategory, int],
                {cat: raw.get(cat, 0) for cat in _ALL_CATEGORIES},
            )
            points.append(
                TimelinePoint(
                    week=row["week"],
                    count=int(row["count"]),
                    by_category=by_category,
                )
            )
        return points
