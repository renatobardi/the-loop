"""Analytics route handlers for incident pattern dashboard — Phase C.2."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.requests import Request

from src.api.deps import get_analytics_service, get_authenticated_user
from src.api.middleware import limiter
from src.api.models.analytics import (
    CategoryStatsResponse,
    SummaryResponse,
    TeamStatsResponse,
    TimelinePointResponse,
)
from src.domain.models import (
    AnalyticsFilter,
    AnalyticsPeriod,
    RootCauseCategory,
)
from src.domain.services import AnalyticsService

router = APIRouter(prefix="/api/v1/incidents/analytics", tags=["analytics"])


def _build_period(
    period: str,
    start_date: str | None,
    end_date: str | None,
) -> AnalyticsPeriod:
    """Parse period + optional date range into AnalyticsPeriod. Raises 400 on invalid input."""
    from datetime import datetime

    allowed = {"week", "month", "quarter", "custom"}
    if period not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period '{period}'. Must be one of: {', '.join(sorted(allowed))}",
        )
    if period == "custom":
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="period=custom requires both start_date and end_date (YYYY-MM-DD)",
            )
        try:
            sd = datetime.fromisoformat(start_date)
            ed = datetime.fromisoformat(end_date)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date and end_date must be ISO date strings (YYYY-MM-DD)",
            ) from exc
        if sd > ed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must not be after end_date",
            )
        return AnalyticsPeriod(value="custom", start_date=sd, end_date=ed)
    return AnalyticsPeriod(value=period)  # type: ignore[arg-type]


def _build_filter(
    team: str | None,
    category: str | None,
    status_filter: str,
) -> AnalyticsFilter:
    """Build AnalyticsFilter from query params. Raises 400 on invalid category/status."""
    allowed_status = {"resolved", "unresolved", "all"}
    if status_filter not in allowed_status:
        valid = ", ".join(sorted(allowed_status))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status_filter}'. Must be one of: {valid}",
        )
    category_enum: RootCauseCategory | None = None
    if category:
        try:
            category_enum = RootCauseCategory(category)
        except ValueError as exc:
            valid = ", ".join(c.value for c in RootCauseCategory)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category '{category}'. Must be one of: {valid}",
            ) from exc
    return AnalyticsFilter(
        team=team or None,
        category=category_enum,
        status=status_filter,  # type: ignore[arg-type]
    )


@router.get("/summary", response_model=SummaryResponse)
@limiter.limit("60/minute")
async def get_analytics_summary(
    request: Request,
    period: str = Query(default="month"),
    team: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> SummaryResponse:
    """Return total/resolved/unresolved counts and average resolution days."""
    ap = _build_period(period, start_date, end_date)
    af = _build_filter(team, category, status)
    summary = await service.get_summary(ap, af)
    return SummaryResponse(
        total=summary.total,
        resolved=summary.resolved,
        unresolved=summary.unresolved,
        avg_resolution_days=summary.avg_resolution_days,
    )


@router.get("/by-category", response_model=list[CategoryStatsResponse])
@limiter.limit("60/minute")
async def get_analytics_by_category(
    request: Request,
    period: str = Query(default="month"),
    team: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[CategoryStatsResponse]:
    """Return incident stats per root cause category, sorted by count descending."""
    ap = _build_period(period, start_date, end_date)
    af = _build_filter(team, category, status)
    stats = await service.get_by_category(ap, af)
    return [
        CategoryStatsResponse(
            category=s.category.value,
            count=s.count,
            percentage=s.percentage,
            avg_severity=s.avg_severity,
            avg_resolution_days=s.avg_resolution_days,
        )
        for s in stats
    ]


@router.get("/by-team", response_model=list[TeamStatsResponse])
@limiter.limit("60/minute")
async def get_analytics_by_team(
    request: Request,
    period: str = Query(default="month"),
    team: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[TeamStatsResponse]:
    """Return incident stats per team, sorted by count descending."""
    ap = _build_period(period, start_date, end_date)
    af = _build_filter(team, category, status)
    stats = await service.get_by_team(ap, af)
    return [
        TeamStatsResponse(
            team=s.team,
            count=s.count,
            top_categories=[c.value for c in s.top_categories],
            avg_resolution_days=s.avg_resolution_days,
        )
        for s in stats
    ]


@router.get("/timeline", response_model=list[TimelinePointResponse])
@limiter.limit("60/minute")
async def get_analytics_timeline(
    request: Request,
    period: str = Query(default="month"),
    team: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[TimelinePointResponse]:
    """Return weekly incident counts with per-category breakdown (12+ months)."""
    ap = _build_period(period, start_date, end_date)
    af = _build_filter(team, category, status)
    points = await service.get_timeline(ap, af)
    return [
        TimelinePointResponse(
            week=p.week.date().isoformat(),
            count=p.count,
            by_category={cat.value: count for cat, count in p.by_category.items()},
        )
        for p in points
    ]
