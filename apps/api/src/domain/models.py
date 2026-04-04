"""Domain models for the Incident module — pure Python, no external dependencies."""

import re
from datetime import date as _Date
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

__all__ = [
    "UNSET",
    "ActionItemStatus",
    "AnalyticsFilter",
    "AnalyticsPeriod",
    "AnalyticsSummary",
    "AttachmentExtractionStatus",
    "AttachmentType",
    "Category",
    "CategoryStats",
    "DetectionMethod",
    "Incident",
    "IncidentActionItem",
    "IncidentAttachment",
    "IncidentResponder",
    "IncidentTimelineEvent",
    "Postmortem",
    "PostmortemStatus",
    "PostmortumSeverity",
    "ResponderRole",
    "RootCauseCategory",
    "RootCauseTemplate",
    "Rule",
    "RuleVersion",
    "RuleVersionStatus",
    "Severity",
    "TeamStats",
    "TimelineEventType",
    "TimelinePoint",
    "User",
    "UserPlan",
]


class Category(StrEnum):
    UNSAFE_REGEX = "unsafe-regex"
    INJECTION = "injection"
    DEPLOYMENT_ERROR = "deployment-error"
    MISSING_SAFETY_CHECK = "missing-safety-check"
    RACE_CONDITION = "race-condition"
    UNSAFE_API_USAGE = "unsafe-api-usage"
    RESOURCE_EXHAUSTION = "resource-exhaustion"
    DATA_CONSISTENCY = "data-consistency"
    MISSING_ERROR_HANDLING = "missing-error-handling"
    CASCADING_FAILURE = "cascading-failure"
    AUTHENTICATION_BYPASS = "authentication-bypass"
    CONFIGURATION_DRIFT = "configuration-drift"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PostmortemStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"


class TimelineEventType(StrEnum):
    DETECTED = "detected"
    ESCALATED = "escalated"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    REVIEWED = "reviewed"
    POSTMORTEM_PUBLISHED = "postmortem_published"


class DetectionMethod(StrEnum):
    MONITORING_ALERT = "monitoring_alert"
    CUSTOMER_REPORT = "customer_report"
    INTERNAL_TEST = "internal_test"
    AUTOMATED_SCAN = "automated_scan"
    MANUAL_DISCOVERY = "manual_discovery"
    EXTERNAL_REPORT = "external_report"


class ResponderRole(StrEnum):
    INCIDENT_COMMANDER = "incident_commander"
    TECHNICAL_LEAD = "technical_lead"
    COMMUNICATION_LEAD = "communication_lead"
    REMEDIATION_LEAD = "remediation_lead"
    RESPONDER = "responder"
    POSTMORTEM_LEAD = "postmortem_lead"


class ActionItemStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionItemPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttachmentExtractionStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AttachmentType(StrEnum):
    POSTMORTEM_DOC = "postmortem_doc"
    LOG_FILE = "log_file"
    SCREENSHOT = "screenshot"
    MONITORING_EXPORT = "monitoring_export"
    RUNBOOK = "runbook"
    CONFIG_SNAPSHOT = "config_snapshot"
    SLACK_EXPORT = "slack_export"
    JIRA_EXPORT = "jira_export"


SEMGREP_RULE_PATTERN = re.compile(r"^[a-z][\w-]+-\d{3}$")


class Incident(BaseModel):
    """Immutable domain entity representing a production incident."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    title: str
    date: _Date | None = None
    source_url: str | None = None
    organization: str | None = None
    category: Category
    subcategory: str | None = None
    failure_mode: str | None = None
    severity: Severity
    affected_languages: list[str] = []
    anti_pattern: str
    code_example: str | None = None
    remediation: str
    static_rule_possible: bool = False
    semgrep_rule_id: str | None = None
    embedding: list[float] | None = None
    tags: list[str] = []
    version: int = 1
    deleted_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID

    # Timestamps (migration 002)
    started_at: datetime | None = None
    detected_at: datetime | None = None
    ended_at: datetime | None = None
    resolved_at: datetime | None = None

    # Operational / postmortem fields (migration 002)
    impact_summary: str | None = None
    customers_affected: int | None = None
    sla_breached: bool = False
    slo_breached: bool = False
    postmortem_status: PostmortemStatus = PostmortemStatus.DRAFT
    postmortem_published_at: datetime | None = None
    postmortem_due_date: _Date | None = None
    lessons_learned: str | None = None
    why_we_were_surprised: str | None = None
    detection_method: DetectionMethod | None = None
    slack_channel_id: str | None = None
    external_tracking_id: str | None = None
    incident_lead_id: UUID | None = None

    # JSONB embedding fields (migration 003)
    raw_content: dict[str, object] | None = None
    tech_context: dict[str, object] | None = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 500:
            msg = "Title must be between 1 and 500 characters"
            raise ValueError(msg)
        return v

    @field_validator("anti_pattern")
    @classmethod
    def anti_pattern_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Anti-pattern must not be empty"
            raise ValueError(msg)
        return v

    @field_validator("remediation")
    @classmethod
    def remediation_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Remediation must not be empty"
            raise ValueError(msg)
        return v

    @field_validator("source_url")
    @classmethod
    def source_url_length(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 2048:
                msg = "Source URL must be at most 2048 characters"
                raise ValueError(msg)
        return v

    @field_validator("organization")
    @classmethod
    def organization_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 255:
            msg = "Organization must be at most 255 characters"
            raise ValueError(msg)
        return v

    @field_validator("subcategory")
    @classmethod
    def subcategory_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            msg = "Subcategory must be at most 100 characters"
            raise ValueError(msg)
        return v

    @field_validator("semgrep_rule_id")
    @classmethod
    def semgrep_rule_id_format(cls, v: str | None) -> str | None:
        if v is not None:
            if len(v) > 50:
                msg = "Semgrep rule ID must be at most 50 characters"
                raise ValueError(msg)
            if not SEMGREP_RULE_PATTERN.match(v):
                msg = "Semgrep rule ID must match format {category}-{NNN}"
                raise ValueError(msg)
        return v

    @field_validator("version")
    @classmethod
    def version_positive(cls, v: int) -> int:
        if v < 1:
            msg = "Version must be >= 1"
            raise ValueError(msg)
        return v

    @field_validator("embedding")
    @classmethod
    def embedding_null_phase_a(cls, v: list[float] | None) -> None:
        if v is not None:
            msg = "Embedding must be NULL in Phase A"
            raise ValueError(msg)
        return None

    @field_validator("customers_affected")
    @classmethod
    def customers_affected_nonneg(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            msg = "customers_affected must be >= 0"
            raise ValueError(msg)
        return v

    @field_validator("affected_languages", "tags")
    @classmethod
    def list_items_not_empty(cls, v: list[str]) -> list[str]:
        return [item for item in v if item.strip()]

    @model_validator(mode="after")
    def temporal_constraints(self) -> "Incident":
        if self.started_at and self.detected_at and self.started_at > self.detected_at:
            msg = "detected_at must not be before started_at"
            raise ValueError(msg)
        if self.ended_at and self.resolved_at and self.ended_at > self.resolved_at:
            msg = "resolved_at must not be before ended_at"
            raise ValueError(msg)
        return self

    @property
    def duration_minutes(self) -> int | None:
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() / 60)
        return None

    @property
    def time_to_detect_minutes(self) -> int | None:
        if self.started_at and self.detected_at:
            return int((self.detected_at - self.started_at).total_seconds() / 60)
        return None

    @property
    def time_to_resolve_minutes(self) -> int | None:
        if self.started_at and self.resolved_at:
            return int((self.resolved_at - self.started_at).total_seconds() / 60)
        return None


class IncidentTimelineEvent(BaseModel):
    """Immutable domain entity for a single timeline event on an incident."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    incident_id: UUID
    event_type: TimelineEventType
    description: str
    occurred_at: datetime
    recorded_by: UUID
    duration_minutes: int | None = None
    external_reference_url: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Description must not be empty"
            raise ValueError(msg)
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_nonneg(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            msg = "duration_minutes must be >= 0"
            raise ValueError(msg)
        return v


class IncidentResponder(BaseModel):
    """Immutable domain entity for a responder on an incident."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    incident_id: UUID
    user_id: UUID
    role: ResponderRole
    joined_at: datetime
    left_at: datetime | None = None
    contribution_summary: str | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def left_after_joined(self) -> "IncidentResponder":
        if self.left_at is not None and self.left_at < self.joined_at:
            msg = "left_at must not be before joined_at"
            raise ValueError(msg)
        return self


class IncidentActionItem(BaseModel):
    """Immutable domain entity for a follow-up action item on an incident."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    incident_id: UUID
    title: str
    description: str | None = None
    owner_id: UUID | None = None
    status: ActionItemStatus = ActionItemStatus.OPEN
    priority: ActionItemPriority = ActionItemPriority.MEDIUM
    due_date: _Date | None = None
    completed_at: datetime | None = None
    completed_by: UUID | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Title must not be empty"
            raise ValueError(msg)
        return v


class IncidentAttachment(BaseModel):
    """Immutable domain entity for a file attachment on an incident."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    incident_id: UUID
    uploaded_by: UUID | None = None
    filename: str
    mime_type: str
    file_size_bytes: int
    gcs_bucket: str
    gcs_object_path: str
    content_text: str | None = None
    extraction_status: AttachmentExtractionStatus = AttachmentExtractionStatus.PENDING
    attachment_type: AttachmentType
    source_system: str | None = None
    source_url: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("file_size_bytes")
    @classmethod
    def file_size_positive(cls, v: int) -> int:
        if v <= 0:
            msg = "file_size_bytes must be > 0"
            raise ValueError(msg)
        return v


# ─── Phase B: API Integration & Versioning ───────────────────────────────────


class RuleVersionStatus(StrEnum):
    """Status of a rule version in the versioning lifecycle."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class Rule(BaseModel):
    """Individual rule definition (immutable once in a version)."""

    model_config = ConfigDict(frozen=True)

    id: str
    languages: list[str]
    message: str
    severity: str  # "ERROR" or "WARNING"
    metadata: dict[str, Any]
    patterns: list[dict[str, Any]]


class RuleVersion(BaseModel):
    """Versioned collection of rules with lifecycle management."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    version: str  # Semantic version: "0.1.0"
    rules: list[Rule]
    status: RuleVersionStatus
    created_at: datetime
    published_by: UUID
    notes: str | None = None
    deprecated_at: datetime | None = None

    @field_validator("version")
    @classmethod
    def validate_semver(cls, v: str) -> str:
        """Validate semantic versioning format (X.Y.Z)."""
        if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", v):
            msg = f"Invalid semantic version format: {v}. Expected: X.Y.Z"
            raise ValueError(msg)
        return v

    @property
    def rules_count(self) -> int:
        """Count of rules in this version."""
        return len(self.rules)


# ─── Phase C: Incident Knowledge Capture (Postmortem) ────────────────────────


class RootCauseCategory(StrEnum):
    """Root cause categories for incident postmortems."""

    CODE_PATTERN = "code_pattern"
    INFRASTRUCTURE = "infrastructure"
    PROCESS_BREAKDOWN = "process_breakdown"
    THIRD_PARTY = "third_party"
    UNKNOWN = "unknown"


class PostmortumSeverity(StrEnum):
    """Severity level for prevention rules (from postmortem)."""

    ERROR = "error"  # Blocks merge in CI/CD
    WARNING = "warning"  # Advisory, non-blocking


class RootCauseTemplate(BaseModel):
    """Pre-filled template for postmortem form."""

    model_config = ConfigDict(frozen=True)

    id: str  # "sql-injection", "n-plus-one", etc.
    category: RootCauseCategory
    title: str  # Human-readable: "SQL Injection"
    description_template: str  # Template with hints
    pattern_example: str | None = None  # Example regex or semgrep pattern
    severity_default: PostmortumSeverity


class Postmortem(BaseModel):
    """Root cause analysis for an incident (immutable once resolved)."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    incident_id: UUID  # Foreign key to Incident
    root_cause_category: RootCauseCategory
    description: str  # 20-2000 chars
    suggested_pattern: str | None = None  # Regex or semgrep pattern (optional)
    team_responsible: str  # "backend", "frontend", etc.
    severity_for_rule: PostmortumSeverity
    related_rule_id: str | None = None  # Reference existing rule (e.g., "injection-001")
    created_by: UUID
    created_at: datetime
    updated_by: UUID | None = None
    updated_at: datetime | None = None
    is_locked: bool = False  # Read-only after incident resolved

    @field_validator("description")
    @classmethod
    def validate_description_length(cls, v: str) -> str:
        """Validate description is between 20-2000 chars."""
        if len(v) < 20:
            msg = "Description must be at least 20 characters"
            raise ValueError(msg)
        if len(v) > 2000:
            msg = "Description must not exceed 2000 characters"
            raise ValueError(msg)
        return v


# ─── Phase C.2: Incident Analytics ───────────────────────────────────────────


class CategoryStats(BaseModel):
    """Aggregated incident statistics for a single root cause category."""

    model_config = ConfigDict(frozen=True)

    category: RootCauseCategory
    count: int
    percentage: float  # 0-100
    avg_severity: float  # 0.5 (warning) or 1.0 (error)
    avg_resolution_days: float | None = None  # None when filtered to unresolved-only


class TeamStats(BaseModel):
    """Aggregated incident statistics for a single team."""

    model_config = ConfigDict(frozen=True)

    team: str
    count: int
    top_categories: list[RootCauseCategory]  # Top 3 per RF-003
    avg_resolution_days: float | None = None  # None when filtered to unresolved-only


class TimelinePoint(BaseModel):
    """Weekly incident count with per-category breakdown."""

    model_config = ConfigDict(frozen=True)

    week: datetime
    count: int
    by_category: dict[RootCauseCategory, int]  # Always all 5 keys (0 for absent)


class AnalyticsSummary(BaseModel):
    """Top-level incident count summary for the selected period."""

    model_config = ConfigDict(frozen=True)

    total: int
    resolved: int
    unresolved: int
    avg_resolution_days: float | None = None  # None when filtered to unresolved-only


class AnalyticsFilter(BaseModel):
    """Filters applied to all analytics queries."""

    model_config = ConfigDict(frozen=True)

    team: str | None = None
    category: RootCauseCategory | None = None
    status: Literal["resolved", "unresolved", "all"] = "all"


class AnalyticsPeriod(BaseModel):
    """Time period selector for analytics queries."""

    model_config = ConfigDict(frozen=True)

    value: Literal["week", "month", "quarter", "custom"]
    start_date: datetime | None = None  # Required when value="custom"
    end_date: datetime | None = None  # Required when value="custom"


# ─── Phase 2: Navigation, Dashboard & User Profile ───────────────────────────


class _UnsetSentinel:
    """Sentinel for distinguishing 'field omitted' from 'explicit None' in partial updates."""

    _instance: "_UnsetSentinel | None" = None

    def __new__(cls) -> "_UnsetSentinel":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"


UNSET = _UnsetSentinel()


class UserPlan(StrEnum):
    """Subscription plan for a user account."""

    FREE = "free"
    BETA = "beta"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(BaseModel):
    """Immutable domain entity representing a registered user."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    firebase_uid: str
    email: str
    display_name: str | None = None
    job_title: str | None = None
    plan: UserPlan = UserPlan.BETA
    created_at: datetime
    updated_at: datetime
