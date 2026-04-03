"""Postmortem route handlers for incident root cause analysis."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from src.adapters.postgres.postmortem_templates import POSTMORTEM_TEMPLATES
from src.api.deps import get_authenticated_user, get_incident_service, get_postmortem_service
from src.api.middleware import limiter
from src.api.models.postmortems import (
    PostmortumCreateRequest,
    PostmortumListResponse,
    PostmortumResponse,
    PostmortumSummaryResponse,
    PostmortumUpdateRequest,
    RootCauseTemplateResponse,
    TemplateListResponse,
)
from src.domain.exceptions import (
    IncidentNotFoundError,
    PostmortumAlreadyExistsError,
    PostmortumLockedError,
    PostmortumNotFoundError,
)
from src.domain.models import PostmortumSeverity, RootCauseCategory
from src.domain.services import IncidentService, PostmortumService

router = APIRouter(prefix="/api/v1", tags=["postmortems"])


async def _get_incident_or_404(incident_id: UUID, incident_service: IncidentService) -> None:
    """Validate incident exists, raise 404 if not."""
    try:
        await incident_service.get_by_id(incident_id)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        ) from e


async def _get_postmortem_or_404(
    postmortem_id: UUID, postmortem_service: PostmortumService
) -> None:
    """Validate postmortem exists, raise 404 if not."""
    try:
        await postmortem_service.get_by_id(postmortem_id)
    except PostmortumNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postmortem not found"
        ) from e


@router.post(
    "/incidents/{incident_id}/postmortem",
    status_code=status.HTTP_201_CREATED,
    response_model=PostmortumResponse,
)
@limiter.limit("60/minute")
async def create_postmortem(
    request: Request,
    incident_id: UUID,
    body: PostmortumCreateRequest,
    postmortem_service: PostmortumService = Depends(get_postmortem_service),
    incident_service: IncidentService = Depends(get_incident_service),
    user_id: UUID = Depends(get_authenticated_user),
) -> PostmortumResponse:
    """Create a postmortem for an incident.

    Only one postmortem per incident allowed. Returns 409 Conflict if postmortem already exists.
    """
    # Validate incident exists
    await _get_incident_or_404(incident_id, incident_service)

    # Create postmortem
    try:
        postmortem = await postmortem_service.create(
            incident_id=incident_id,
            root_cause_category=RootCauseCategory(body.root_cause_category),
            description=body.description,
            team_responsible=body.team_responsible,
            severity_for_rule=PostmortumSeverity(body.severity_for_rule),
            created_by=user_id,
            suggested_pattern=body.suggested_pattern,
            related_rule_id=body.related_rule_id,
        )
    except PostmortumAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Postmortem already exists for this incident. Use PUT to update.",
        ) from e

    return PostmortumResponse.from_domain(postmortem)


@router.get(
    "/incidents/{incident_id}/postmortem",
    response_model=PostmortumResponse,
)
@limiter.limit("120/minute")
async def get_postmortem_by_incident(
    request: Request,
    incident_id: UUID,
    postmortem_service: PostmortumService = Depends(get_postmortem_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> PostmortumResponse:
    """Get postmortem for an incident (1:1 relationship).

    Returns 404 if incident not found or if no postmortem exists yet.
    """
    # Validate incident exists
    await _get_incident_or_404(incident_id, incident_service)

    # Get postmortem
    postmortem = await postmortem_service.get_by_incident_id(incident_id)
    if postmortem is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No postmortem exists for this incident yet.",
        )

    return PostmortumResponse.from_domain(postmortem)


@router.get(
    "/postmortems/{postmortem_id}",
    response_model=PostmortumResponse,
)
@limiter.limit("120/minute")
async def get_postmortem(
    request: Request,
    postmortem_id: UUID,
    postmortem_service: PostmortumService = Depends(get_postmortem_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> PostmortumResponse:
    """Get a postmortem by ID."""
    try:
        postmortem = await postmortem_service.get_by_id(postmortem_id)
    except PostmortumNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postmortem not found"
        ) from e

    return PostmortumResponse.from_domain(postmortem)


@router.put(
    "/postmortems/{postmortem_id}",
    response_model=PostmortumResponse,
)
@limiter.limit("60/minute")
async def update_postmortem(
    request: Request,
    postmortem_id: UUID,
    body: PostmortumUpdateRequest,
    postmortem_service: PostmortumService = Depends(get_postmortem_service),
    user_id: UUID = Depends(get_authenticated_user),
) -> PostmortumResponse:
    """Update a postmortem.

    Returns 403 Forbidden if postmortem is locked (after incident resolution).
    """
    # Validate postmortem exists
    await _get_postmortem_or_404(postmortem_id, postmortem_service)

    # Prepare update data
    update_fields = {}
    if body.root_cause_category is not None:
        update_fields["root_cause_category"] = body.root_cause_category
    if body.description is not None:
        update_fields["description"] = body.description
    if body.team_responsible is not None:
        update_fields["team_responsible"] = body.team_responsible
    if body.severity_for_rule is not None:
        update_fields["severity_for_rule"] = body.severity_for_rule
    if body.suggested_pattern is not None:
        update_fields["suggested_pattern"] = body.suggested_pattern
    if body.related_rule_id is not None:
        update_fields["related_rule_id"] = body.related_rule_id

    # Update postmortem
    try:
        postmortem = await postmortem_service.update(postmortem_id, **update_fields)
    except PostmortumLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Postmortem is locked after incident resolution. Cannot modify.",
        ) from e
    except PostmortumNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postmortem not found"
        ) from e

    return PostmortumResponse.from_domain(postmortem)


@router.post(
    "/postmortems/{postmortem_id}/lock",
    response_model=PostmortumResponse,
)
@limiter.limit("60/minute")
async def lock_postmortem(
    request: Request,
    postmortem_id: UUID,
    postmortem_service: PostmortumService = Depends(get_postmortem_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> PostmortumResponse:
    """Lock a postmortem after incident resolution.

    Locked postmortems become immutable (read-only). Typically called when incident transitions to resolved state.
    """
    # Validate postmortem exists
    await _get_postmortem_or_404(postmortem_id, postmortem_service)

    # Lock postmortem
    try:
        postmortem = await postmortem_service.lock(postmortem_id)
    except PostmortumNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Postmortem not found"
        ) from e

    return PostmortumResponse.from_domain(postmortem)


@router.get(
    "/postmortem-templates",
    response_model=TemplateListResponse,
)
@limiter.limit("120/minute")
async def list_templates(
    request: Request,
    _user_id: UUID = Depends(get_authenticated_user),
) -> TemplateListResponse:
    """List all available root cause templates for postmortem form.

    Templates are hardcoded in Phase C.1 MVP. Dynamic templates added in Spec-015.
    """
    templates = [
        RootCauseTemplateResponse(
            id=template.id,
            category=template.category.value,
            title=template.title,
            description_template=template.description_template,
            pattern_example=template.pattern_example,
            severity_default=template.severity_default.value,
        )
        for template in POSTMORTEM_TEMPLATES.values()
    ]

    return TemplateListResponse(templates=templates, count=len(templates))


@router.get(
    "/postmortems",
    response_model=PostmortumListResponse,
)
@limiter.limit("120/minute")
async def list_postmortems(
    request: Request,
    postmortem_service: PostmortumService = Depends(get_postmortem_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> PostmortumListResponse:
    """List all postmortems for analytics and reporting.

    Returns summaries ordered by created_at descending (newest first).
    """
    postmortems = await postmortem_service.list_all()

    summaries = [
        PostmortumSummaryResponse(
            incident_id=p.incident_id,
            root_cause_category=p.root_cause_category.value,
            team_responsible=p.team_responsible,
            severity_for_rule=p.severity_for_rule.value,
            created_at=p.created_at,
            is_locked=p.is_locked,
        )
        for p in postmortems
    ]

    return PostmortumListResponse(items=summaries, total=len(summaries))
