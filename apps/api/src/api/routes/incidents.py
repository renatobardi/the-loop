"""CRUD route handlers for incidents."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from starlette.requests import Request

from src.api.deps import get_authenticated_user, get_incident_service
from src.api.middleware import limiter
from src.domain.exceptions import (
    DuplicateSourceUrlError,
    IncidentHasActiveRuleError,
    IncidentNotFoundError,
    OptimisticLockError,
)
from src.domain.models import SEMGREP_RULE_PATTERN, Category, Incident, Severity
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
        page=page, per_page=per_page, category=category, severity=severity, keyword=q,
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
