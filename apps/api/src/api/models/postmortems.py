"""Request/response models for postmortems API — Phase C knowledge capture."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PostmortumCreateRequest(BaseModel):
    """Request body for POST /api/v1/incidents/{id}/postmortem."""

    root_cause_category: str = Field(
        ...,
        description=(
            "Root cause category (code_pattern, infrastructure, "
            "process_breakdown, third_party, unknown)"
        ),
    )
    description: str = Field(
        ...,
        description="Detailed analysis (20-2000 characters)",
        min_length=20,
        max_length=2000,
    )
    team_responsible: str = Field(
        ...,
        description="Team accountable for prevention (e.g., 'backend', 'security')",
        min_length=1,
        max_length=255,
    )
    severity_for_rule: str = Field(
        ...,
        description="Severity for prevention rule (error=blocks merge, warning=advisory)",
    )
    suggested_pattern: str | None = Field(
        None,
        description="Optional regex or semgrep pattern to detect this issue",
        max_length=1000,
    )
    related_rule_id: str | None = Field(
        None,
        description="Optional reference to existing rule (e.g., 'injection-001')",
        max_length=100,
    )

    @field_validator("root_cause_category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is in allowed set."""
        valid = {"code_pattern", "infrastructure", "process_breakdown", "third_party", "unknown"}
        if v not in valid:
            msg = f"Invalid category: {v}. Must be one of {valid}"
            raise ValueError(msg)
        return v

    @field_validator("severity_for_rule")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity is error or warning."""
        valid = {"error", "warning"}
        if v not in valid:
            msg = f"Invalid severity: {v}. Must be 'error' or 'warning'"
            raise ValueError(msg)
        return v


class PostmortumUpdateRequest(BaseModel):
    """Request body for PUT /api/v1/postmortems/{id}."""

    description: str | None = Field(
        None,
        description="Updated analysis (20-2000 characters)",
        min_length=20,
        max_length=2000,
    )
    team_responsible: str | None = Field(
        None,
        description="Updated team responsible",
        min_length=1,
        max_length=255,
    )
    suggested_pattern: str | None = Field(
        None,
        description="Updated regex or semgrep pattern",
        max_length=1000,
    )
    root_cause_category: str | None = Field(
        None,
        description="Updated category",
    )
    severity_for_rule: str | None = Field(
        None,
        description="Updated severity (error or warning)",
    )
    related_rule_id: str | None = Field(
        None,
        description="Updated rule reference",
        max_length=100,
    )

    @field_validator("root_cause_category")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        """Validate category if provided."""
        if v is None:
            return None
        valid = {"code_pattern", "infrastructure", "process_breakdown", "third_party", "unknown"}
        if v not in valid:
            msg = f"Invalid category: {v}. Must be one of {valid}"
            raise ValueError(msg)
        return v

    @field_validator("severity_for_rule")
    @classmethod
    def validate_severity(cls, v: str | None) -> str | None:
        """Validate severity if provided."""
        if v is None:
            return None
        valid = {"error", "warning"}
        if v not in valid:
            msg = f"Invalid severity: {v}. Must be 'error' or 'warning'"
            raise ValueError(msg)
        return v


class PostmortumResponse(BaseModel):
    """Response body for GET /api/v1/postmortems/{id} or POST/PUT responses."""

    id: UUID
    incident_id: UUID
    root_cause_category: str
    description: str
    suggested_pattern: str | None = None
    team_responsible: str
    severity_for_rule: str
    related_rule_id: str | None = None
    created_by: UUID
    created_at: datetime
    updated_by: UUID | None = None
    updated_at: datetime | None = None
    is_locked: bool

    @classmethod
    def from_domain(cls, postmortem: object) -> "PostmortumResponse":
        """Convert domain Postmortem to API response."""
        # Avoid circular imports; assume postmortem has these attributes
        return cls(
            id=postmortem.id,  # type: ignore[attr-defined]
            incident_id=postmortem.incident_id,  # type: ignore[attr-defined]
            root_cause_category=postmortem.root_cause_category.value,  # type: ignore[attr-defined]
            description=postmortem.description,  # type: ignore[attr-defined]
            suggested_pattern=postmortem.suggested_pattern,  # type: ignore[attr-defined]
            team_responsible=postmortem.team_responsible,  # type: ignore[attr-defined]
            severity_for_rule=postmortem.severity_for_rule.value,  # type: ignore[attr-defined]
            related_rule_id=postmortem.related_rule_id,  # type: ignore[attr-defined]
            created_by=postmortem.created_by,  # type: ignore[attr-defined]
            created_at=postmortem.created_at,  # type: ignore[attr-defined]
            updated_by=postmortem.updated_by,  # type: ignore[attr-defined]
            updated_at=postmortem.updated_at,  # type: ignore[attr-defined]
            is_locked=postmortem.is_locked,  # type: ignore[attr-defined]
        )


class RootCauseTemplateResponse(BaseModel):
    """Response for a single template in template list."""

    id: str
    category: str
    title: str
    description_template: str
    pattern_example: str | None = None
    severity_default: str


class TemplateListResponse(BaseModel):
    """Response body for GET /api/v1/postmortem-templates."""

    templates: list[RootCauseTemplateResponse]
    count: int


class PostmortumSummaryResponse(BaseModel):
    """Response body for analytics summary endpoint."""

    incident_id: UUID
    root_cause_category: str
    team_responsible: str
    severity_for_rule: str
    created_at: datetime
    is_locked: bool


class PostmortumListResponse(BaseModel):
    """Response body for GET /api/v1/postmortems (analytics listing)."""

    items: list[PostmortumSummaryResponse]
    total: int
