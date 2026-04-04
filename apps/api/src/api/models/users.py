"""Request/response models for users API — Phase 2 nav/dashboard/profile."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator
from src.domain.models import User


class UserResponse(BaseModel):
    """Response model for user profile endpoints."""

    id: UUID
    email: str
    display_name: str | None
    job_title: str | None
    plan: str
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            job_title=user.job_title,
            plan=user.plan.value,
            created_at=user.created_at,
        )


class UserUpdateRequest(BaseModel):
    """Request body for PATCH /api/v1/users/me.

    All fields are optional. Omitting a field leaves it unchanged.
    Sending explicit null for display_name returns 422.
    """

    display_name: str | None = None
    job_title: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_null_display_name(cls, data: Any) -> Any:
        """Distinguish explicit null (→ 422) from omitted field (→ None, don't update)."""
        if isinstance(data, dict) and "display_name" in data and data["display_name"] is None:
            raise ValueError("display_name cannot be null; omit the field to leave it unchanged")
        return data

    @field_validator("display_name")
    @classmethod
    def display_name_not_empty(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) == 0:
            raise ValueError("display_name cannot be empty string")
        return v
