"""Request/response models for rules API — Phase B integration."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RuleData(BaseModel):
    """Individual rule within a version."""

    id: str
    languages: list[str]
    message: str
    severity: str
    metadata: dict[str, Any]
    patterns: list[dict[str, Any]]


class PublishRulesRequest(BaseModel):
    """Request body for POST /api/v1/rules/publish."""

    version: str = Field(..., description="Semantic version (e.g., '0.2.0')")
    rules: list[RuleData] = Field(..., description="Array of rule definitions")
    notes: str | None = Field(None, description="Optional release notes")


class RuleVersionResponse(BaseModel):
    """Response body for GET /api/v1/rules/latest or /api/v1/rules/{version}."""

    version: str
    rules_count: int
    created_at: datetime
    status: str
    rules: list[RuleData]
    published_by: str | None = None
    notes: str | None = None
    deprecated_at: datetime | None = None


class VersionSummary(BaseModel):
    """Summary of a rule version (for list endpoint)."""

    version: str
    status: str
    created_at: datetime
    rules_count: int
    deprecated_at: datetime | None = None


class VersionListResponse(BaseModel):
    """Response body for GET /api/v1/rules/versions."""

    versions: list[VersionSummary]


class PublishRulesResponse(BaseModel):
    """Response body for POST /api/v1/rules/publish (201 Created)."""

    message: str
    version: str
    created_at: datetime
    rules_count: int


class DeprecateRulesRequest(BaseModel):
    """Request body for POST /api/v1/rules/deprecate."""

    version: str = Field(..., description="Semantic version to deprecate (e.g., '0.1.0')")

    @field_validator("version")
    @classmethod
    def validate_semver(cls, v: str) -> str:
        """Validate that version matches semantic versioning pattern X.Y.Z."""
        import re

        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", v):
            msg = f"Invalid semver format: {v}. Expected X.Y.Z (e.g., '0.1.0')"
            raise ValueError(msg)
        return v


class DeprecateRulesResponse(BaseModel):
    """Response body for POST /api/v1/rules/deprecate (200 OK)."""

    message: str
    version: str
    deprecated_at: datetime
