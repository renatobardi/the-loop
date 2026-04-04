"""Port definition for the Analytics repository."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from src.domain.models import (
    AnalyticsFilter,
    AnalyticsSummary,
    CategoryStats,
    TeamStats,
    TimelinePoint,
)


class AnalyticsRepoPort(Protocol):
    """Repository operations for incident analytics aggregations."""

    async def get_summary(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> AnalyticsSummary:
        """Return total/resolved/unresolved counts and avg resolution days."""
        ...

    async def get_by_category(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> list[CategoryStats]:
        """Return incident stats grouped by root_cause_category, ordered by count DESC."""
        ...

    async def get_by_team(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> list[TeamStats]:
        """Return incident stats grouped by team_responsible, ordered by count DESC."""
        ...

    async def get_timeline(
        self, start: datetime, end: datetime, filters: AnalyticsFilter
    ) -> list[TimelinePoint]:
        """Return weekly incident counts with per-category breakdown, ordered by week ASC."""
        ...
