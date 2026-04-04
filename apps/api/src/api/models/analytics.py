"""Request/response models for analytics API — Phase C.2 dashboard."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator


class AnalyticsFilterRequest(BaseModel):
    """Query parameters shared by all analytics endpoints."""

    period: str = "month"
    team: str | None = None
    category: str | None = None
    status: str = "all"
    start_date: datetime | None = None  # Required when period="custom"
    end_date: datetime | None = None  # Required when period="custom"

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        allowed = {"week", "month", "quarter", "custom"}
        if v not in allowed:
            msg = f"period must be one of {sorted(allowed)}"
            raise ValueError(msg)
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"resolved", "unresolved", "all"}
        if v not in allowed:
            msg = f"status must be one of {sorted(allowed)}"
            raise ValueError(msg)
        return v


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
