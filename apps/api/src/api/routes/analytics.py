"""Analytics route handlers for incident pattern dashboard — Phase C.2 + Spec-019."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.requests import Request

from src.api.deps import get_analytics_service, get_authenticated_user
from src.api.middleware import limiter
from src.api.models.analytics import (
    CategoryStatsResponse,
    RuleEffectivenessResponse,
    SeverityTrendResponse,
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
    from datetime import UTC, datetime

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
            # Parse date-only strings (YYYY-MM-DD) and anchor to start/end of day in UTC.
            # fromisoformat("2026-04-04") produces midnight (00:00:00) — without end-of-day
            # anchoring, same-day postmortems are excluded by the `< :end` condition.
            sd = datetime.fromisoformat(start_date).replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC
            )
            ed = datetime.fromisoformat(end_date).replace(
                hour=23, minute=59, second=59, microsecond=999999, tzinfo=UTC
            )
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
    team: list[str],
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
        teams=team,
        category=category_enum,
        status=status_filter,  # type: ignore[arg-type]
    )


@router.get("/summary", response_model=SummaryResponse)
@limiter.limit("60/minute")
async def get_analytics_summary(
    request: Request,
    period: str = Query(default="month"),
    team: list[str] = Query(default=[]),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> SummaryResponse:
    """Return aggregate incident counts and average resolution time.

    Counts postmortems (joined to their parent incident) within the requested
    period and optional filters.  `avg_resolution_days` is null when no
    resolved incidents exist in the window.

    Raises 400 for invalid period, status, or category values.
    Raises 401 when the Firebase token is missing or expired.
    """
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
    team: list[str] = Query(default=[]),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[CategoryStatsResponse]:
    """Return incident stats grouped by root cause category.

    Each item includes count, percentage share of the filtered universe,
    avg_severity (0.5-1.0 scale from severity_for_rule), and avg_resolution_days.
    Results are sorted by count descending.  Returns an empty list when no
    postmortems exist in the requested period.

    Raises 400 for invalid period, status, or category values.
    Raises 401 when the Firebase token is missing or expired.
    """
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
    team: list[str] = Query(default=[]),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[TeamStatsResponse]:
    """Return incident stats grouped by team_responsible.

    Each item includes count, top_categories (up to 3 most frequent root causes
    for that team, derived from jsonb aggregation), and avg_resolution_days.
    Results are sorted by count descending.  Returns an empty list when no
    postmortems exist in the requested period.

    Raises 400 for invalid period, status, or category values.
    Raises 401 when the Firebase token is missing or expired.
    """
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
    team: list[str] = Query(default=[]),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[TimelinePointResponse]:
    """Return weekly incident counts with per-category breakdown.

    Each point represents one ISO week (DATE_TRUNC('week', created_at)).  The
    by_category dict always contains all 5 RootCauseCategory keys; missing
    categories are filled with 0.  Points are sorted ascending by week.

    Use period=quarter or period=custom for multi-month views (52+ weeks of
    data are available for charting long-term trends).

    Raises 400 for invalid period, status, or category values.
    Raises 401 when the Firebase token is missing or expired.
    """
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


@router.get("/severity-trend", response_model=list[SeverityTrendResponse])
@limiter.limit("60/minute")
async def get_analytics_severity_trend(
    request: Request,
    period: str = Query(default="month"),
    team: list[str] = Query(default=[]),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[SeverityTrendResponse]:
    """Return weekly ERROR vs WARNING counts for severity trend chart.

    Each point represents one ISO week aggregated from postmortems.severity_for_rule.
    Points are sorted ascending by week. Used to render the stacked area chart (US3).

    Raises 400 for invalid period, status, or category values.
    Raises 401 when the Firebase token is missing or expired.
    """
    ap = _build_period(period, start_date, end_date)
    af = _build_filter(team, category, status)
    points = await service.get_severity_trend(ap, af)
    return [
        SeverityTrendResponse(
            week=p.week.date().isoformat(),
            error_count=p.error_count,
            warning_count=p.warning_count,
        )
        for p in points
    ]


@router.get("/top-rules", response_model=list[RuleEffectivenessResponse])
@limiter.limit("60/minute")
async def get_analytics_top_rules(
    request: Request,
    period: str = Query(default="month"),
    team: list[str] = Query(default=[]),
    category: str | None = Query(default=None),
    status: str = Query(default="all"),
    top_n: int = Query(default=5, ge=1, le=20),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    _user_id: UUID = Depends(get_authenticated_user),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[RuleEffectivenessResponse]:
    """Return top N rules ranked by incident count with average severity.

    Only includes postmortems where related_rule_id is set. Used to render
    the Rule Effectiveness Card (US4). Defaults to top 5, max 20.

    Raises 400 for invalid period, status, or category values.
    Raises 401 when the Firebase token is missing or expired.
    """
    ap = _build_period(period, start_date, end_date)
    af = _build_filter(team, category, status)
    rules = await service.get_top_rules(ap, af, top_n)
    return [
        RuleEffectivenessResponse(
            rule_id=r.rule_id,
            incident_count=r.incident_count,
            avg_severity=r.avg_severity,
        )
        for r in rules
    ]
