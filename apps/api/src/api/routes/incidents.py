"""CRUD route handlers for incidents."""

from datetime import date as _Date  # noqa: N812
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from starlette.requests import Request

from src.api.deps import get_authenticated_user, get_incident_service
from src.api.middleware import limiter
from src.domain.exceptions import (
    DuplicateSourceUrlError,
    IncidentHasActiveRuleError,
    IncidentMissingPostmortumError,
    IncidentNotFoundError,
    OptimisticLockError,
)
from src.domain.models import (
    SEMGREP_RULE_PATTERN,
    Category,
    DetectionMethod,
    Incident,
    PostmortemStatus,
    Severity,
)
from src.domain.services import IncidentService

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


def _validate_semgrep_rule_id(v: str | None) -> str | None:
    if v is not None:
        if len(v) > 50:
            msg = "Semgrep rule ID must be at most 50 characters"
            raise ValueError(msg)
        if not SEMGREP_RULE_PATTERN.match(v):
            msg = "Semgrep rule ID must match format {category}-{NNN} (e.g. injection-001)"
            raise ValueError(msg)
    return v


class IncidentCreateRequest(BaseModel):
    title: str
    date: str | None = None
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
    tags: list[str] = []
    started_at: datetime | None = None
    detected_at: datetime | None = None
    ended_at: datetime | None = None
    resolved_at: datetime | None = None
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
    raw_content: dict[str, object] | None = None
    tech_context: dict[str, object] | None = None

    @field_validator("semgrep_rule_id")
    @classmethod
    def semgrep_rule_id_format(cls, v: str | None) -> str | None:
        return _validate_semgrep_rule_id(v)


class IncidentUpdateRequest(BaseModel):
    title: str | None = None
    date: str | None = None
    source_url: str | None = None
    organization: str | None = None
    category: Category | None = None
    subcategory: str | None = None
    failure_mode: str | None = None
    severity: Severity | None = None
    affected_languages: list[str] | None = None
    anti_pattern: str | None = None
    code_example: str | None = None
    remediation: str | None = None
    static_rule_possible: bool | None = None
    semgrep_rule_id: str | None = None
    tags: list[str] | None = None
    version: int
    started_at: datetime | None = None
    detected_at: datetime | None = None
    ended_at: datetime | None = None
    resolved_at: datetime | None = None
    impact_summary: str | None = None
    customers_affected: int | None = None
    sla_breached: bool | None = None
    slo_breached: bool | None = None
    postmortem_status: PostmortemStatus | None = None
    postmortem_published_at: datetime | None = None
    postmortem_due_date: _Date | None = None
    lessons_learned: str | None = None
    why_we_were_surprised: str | None = None
    detection_method: DetectionMethod | None = None
    slack_channel_id: str | None = None
    external_tracking_id: str | None = None
    incident_lead_id: UUID | None = None
    raw_content: dict[str, object] | None = None
    tech_context: dict[str, object] | None = None

    @field_validator("semgrep_rule_id")
    @classmethod
    def semgrep_rule_id_format(cls, v: str | None) -> str | None:
        return _validate_semgrep_rule_id(v)

    @field_validator("version")
    @classmethod
    def version_required(cls, v: int) -> int:
        if v < 1:
            msg = "Version must be >= 1"
            raise ValueError(msg)
        return v


class IncidentResponse(BaseModel):
    id: UUID
    title: str
    date: str | None
    source_url: str | None
    organization: str | None
    category: str
    subcategory: str | None
    failure_mode: str | None
    severity: str
    affected_languages: list[str]
    anti_pattern: str
    code_example: str | None
    remediation: str
    static_rule_possible: bool
    semgrep_rule_id: str | None
    embedding: list[float] | None
    tags: list[str]
    version: int
    deleted_at: str | None
    created_at: str
    updated_at: str
    created_by: UUID
    started_at: str | None
    detected_at: str | None
    ended_at: str | None
    resolved_at: str | None
    duration_minutes: int | None
    time_to_detect_minutes: int | None
    time_to_resolve_minutes: int | None
    impact_summary: str | None
    customers_affected: int | None
    sla_breached: bool
    slo_breached: bool
    postmortem_status: str
    postmortem_published_at: str | None
    postmortem_due_date: str | None
    lessons_learned: str | None
    why_we_were_surprised: str | None
    detection_method: str | None
    slack_channel_id: str | None
    external_tracking_id: str | None
    incident_lead_id: UUID | None
    raw_content: dict[str, object] | None
    tech_context: dict[str, object] | None

    @classmethod
    def from_domain(cls, incident: Incident) -> "IncidentResponse":
        return cls(
            id=incident.id,
            title=incident.title,
            date=str(incident.date) if incident.date else None,
            source_url=incident.source_url,
            organization=incident.organization,
            category=incident.category.value,
            subcategory=incident.subcategory,
            failure_mode=incident.failure_mode,
            severity=incident.severity.value,
            affected_languages=incident.affected_languages,
            anti_pattern=incident.anti_pattern,
            code_example=incident.code_example,
            remediation=incident.remediation,
            static_rule_possible=incident.static_rule_possible,
            semgrep_rule_id=incident.semgrep_rule_id,
            embedding=None,
            tags=incident.tags,
            version=incident.version,
            deleted_at=incident.deleted_at.isoformat() if incident.deleted_at else None,
            created_at=incident.created_at.isoformat(),
            updated_at=incident.updated_at.isoformat(),
            created_by=incident.created_by,
            started_at=incident.started_at.isoformat() if incident.started_at else None,
            detected_at=incident.detected_at.isoformat() if incident.detected_at else None,
            ended_at=incident.ended_at.isoformat() if incident.ended_at else None,
            resolved_at=incident.resolved_at.isoformat() if incident.resolved_at else None,
            duration_minutes=incident.duration_minutes,
            time_to_detect_minutes=incident.time_to_detect_minutes,
            time_to_resolve_minutes=incident.time_to_resolve_minutes,
            impact_summary=incident.impact_summary,
            customers_affected=incident.customers_affected,
            sla_breached=incident.sla_breached,
            slo_breached=incident.slo_breached,
            postmortem_status=incident.postmortem_status.value,
            postmortem_published_at=(
                incident.postmortem_published_at.isoformat()
                if incident.postmortem_published_at
                else None
            ),
            postmortem_due_date=(
                str(incident.postmortem_due_date) if incident.postmortem_due_date else None
            ),
            lessons_learned=incident.lessons_learned,
            why_we_were_surprised=incident.why_we_were_surprised,
            detection_method=(
                incident.detection_method.value if incident.detection_method else None
            ),
            slack_channel_id=incident.slack_channel_id,
            external_tracking_id=incident.external_tracking_id,
            incident_lead_id=incident.incident_lead_id,
            raw_content=incident.raw_content,
            tech_context=incident.tech_context,
        )


class PaginatedResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    page: int
    per_page: int


@router.post("", status_code=status.HTTP_201_CREATED, response_model=IncidentResponse)
@limiter.limit("60/minute")
async def create_incident(
    request: Request,
    body: IncidentCreateRequest,
    service: IncidentService = Depends(get_incident_service),
    user_id: UUID = Depends(get_authenticated_user),
) -> IncidentResponse:
    try:
        incident = await service.create(
            title=body.title,
            category=body.category,
            severity=body.severity,
            anti_pattern=body.anti_pattern,
            remediation=body.remediation,
            created_by=user_id,
            date=body.date,
            source_url=body.source_url,
            organization=body.organization,
            subcategory=body.subcategory,
            failure_mode=body.failure_mode,
            affected_languages=body.affected_languages,
            code_example=body.code_example,
            static_rule_possible=body.static_rule_possible,
            semgrep_rule_id=body.semgrep_rule_id,
            tags=body.tags,
            started_at=body.started_at,
            detected_at=body.detected_at,
            ended_at=body.ended_at,
            resolved_at=body.resolved_at,
            impact_summary=body.impact_summary,
            customers_affected=body.customers_affected,
            sla_breached=body.sla_breached,
            slo_breached=body.slo_breached,
            postmortem_status=body.postmortem_status,
            postmortem_published_at=body.postmortem_published_at,
            postmortem_due_date=body.postmortem_due_date,
            lessons_learned=body.lessons_learned,
            why_we_were_surprised=body.why_we_were_surprised,
            detection_method=body.detection_method,
            slack_channel_id=body.slack_channel_id,
            external_tracking_id=body.external_tracking_id,
            incident_lead_id=body.incident_lead_id,
            raw_content=body.raw_content,
            tech_context=body.tech_context,
        )
    except DuplicateSourceUrlError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "source_url already exists", "source_url": e.source_url},
        ) from e
    return IncidentResponse.from_domain(incident)


@router.get("", response_model=PaginatedResponse)
@limiter.limit("60/minute")
async def list_incidents(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Category | None = None,
    severity: Severity | None = None,
    q: str | None = None,
    service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> PaginatedResponse:
    items, total = await service.list_incidents(
        page=page,
        per_page=per_page,
        category=category,
        severity=severity,
        keyword=q,
    )
    return PaginatedResponse(
        items=[IncidentResponse.from_domain(i) for i in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
@limiter.limit("60/minute")
async def get_incident(
    request: Request,
    incident_id: UUID,
    service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> IncidentResponse:
    try:
        incident = await service.get_by_id(incident_id)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        ) from e
    return IncidentResponse.from_domain(incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
@limiter.limit("60/minute")
async def update_incident(
    request: Request,
    incident_id: UUID,
    body: IncidentUpdateRequest,
    service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> IncidentResponse:
    fields = body.model_dump(exclude_unset=True, exclude={"version"})
    try:
        incident = await service.update(incident_id, body.version, **fields)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        ) from e
    except OptimisticLockError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": "Incident was modified by another process",
                "current_version": e.current_version,
            },
        ) from e
    except IncidentHasActiveRuleError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Cannot change category while semgrep_rule_id is set"},
        ) from e
    except IncidentMissingPostmortumError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": "Cannot resolve incident without postmortem",
                "message": f"Create a postmortem at POST /api/v1/incidents/{incident_id}/postmortem first",
            },
        ) from e
    except DuplicateSourceUrlError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "source_url already exists", "source_url": e.source_url},
        ) from e
    return IncidentResponse.from_domain(incident)


@router.delete("/{incident_id}")
@limiter.limit("60/minute")
async def delete_incident(
    request: Request,
    incident_id: UUID,
    service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> dict[str, str]:
    try:
        await service.soft_delete(incident_id)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        ) from e
    except IncidentHasActiveRuleError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": "Cannot delete incident with active Semgrep rule",
                "semgrep_rule_id": e.semgrep_rule_id,
            },
        ) from e
    return {"detail": "Incident deleted", "id": str(incident_id)}
