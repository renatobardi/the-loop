"""Request/response models for analytics API — Phase C.2 dashboard."""

from __future__ import annotations

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    """Response for GET /analytics/summary."""

    total: int
    resolved: int
    unresolved: int
    avg_resolution_days: float | None = None


class CategoryStatsResponse(BaseModel):
    """Single category entry for GET /analytics/by-category."""

    category: str
    count: int
    percentage: float
    avg_severity: float
    avg_resolution_days: float | None = None


class TeamStatsResponse(BaseModel):
    """Single team entry for GET /analytics/by-team."""

    team: str
    count: int
    top_categories: list[str]
    avg_resolution_days: float | None = None


class TimelinePointResponse(BaseModel):
    """Single weekly point for GET /analytics/timeline."""

    week: str  # ISO date string
    count: int
    by_category: dict[str, int]


class SeverityTrendResponse(BaseModel):
    """Single weekly point for GET /analytics/severity-trend."""

    week: str  # ISO date string YYYY-MM-DD
    error_count: int
    warning_count: int


class RuleEffectivenessResponse(BaseModel):
    """Single rule entry for GET /analytics/top-rules."""

    rule_id: str
    incident_count: int
    avg_severity: float  # 0.5 (warning) or 1.0 (error)
