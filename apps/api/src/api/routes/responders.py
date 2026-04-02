"""Responder route handlers for incidents."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from starlette.requests import Request

from src.api.deps import get_authenticated_user, get_incident_service, get_responder_service
from src.api.middleware import limiter
from src.domain.exceptions import (
    DuplicateResponderError,
    IncidentNotFoundError,
    ResponderNotFoundError,
)
from src.domain.models import IncidentResponder, ResponderRole
from src.domain.services import IncidentService, ResponderService

router = APIRouter(prefix="/api/v1/incidents/{incident_id}/responders", tags=["responders"])


class ResponderAddRequest(BaseModel):
    user_id: UUID
    role: ResponderRole
    joined_at: datetime | None = None
    contribution_summary: str | None = None


class ResponderUpdateRequest(BaseModel):
    role: ResponderRole | None = None
    left_at: datetime | None = None
    contribution_summary: str | None = None


class ResponderResponse(BaseModel):
    id: UUID
    incident_id: UUID
    user_id: UUID
    role: str
    joined_at: str
    left_at: str | None
    contribution_summary: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, r: IncidentResponder) -> "ResponderResponse":
        return cls(
            id=r.id,
            incident_id=r.incident_id,
            user_id=r.user_id,
            role=r.role.value,
            joined_at=r.joined_at.isoformat(),
            left_at=r.left_at.isoformat() if r.left_at else None,
            contribution_summary=r.contribution_summary,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )


class ResponderListResponse(BaseModel):
    items: list[ResponderResponse]
    total: int


async def _get_incident_or_404(
    incident_id: UUID, incident_service: IncidentService
) -> None:
    try:
        await incident_service.get_by_id(incident_id)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        ) from e


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResponderResponse)
@limiter.limit("60/minute")
async def add_responder(
    request: Request,
    incident_id: UUID,
    body: ResponderAddRequest,
    responder_service: ResponderService = Depends(get_responder_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> ResponderResponse:
    await _get_incident_or_404(incident_id, incident_service)
    try:
        responder = await responder_service.add_responder(
            incident_id=incident_id,
            user_id=body.user_id,
            role=body.role,
            joined_at=body.joined_at,
            contribution_summary=body.contribution_summary,
        )
    except DuplicateResponderError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Responder already exists for this incident",
        ) from e
    return ResponderResponse.from_domain(responder)


@router.get("", response_model=ResponderListResponse)
@limiter.limit("60/minute")
async def list_responders(
    request: Request,
    incident_id: UUID,
    responder_service: ResponderService = Depends(get_responder_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> ResponderListResponse:
    await _get_incident_or_404(incident_id, incident_service)
    responders = await responder_service.list_responders(incident_id)
    return ResponderListResponse(
        items=[ResponderResponse.from_domain(r) for r in responders],
        total=len(responders),
    )


@router.put("/{responder_id}", response_model=ResponderResponse)
@limiter.limit("60/minute")
async def update_responder(
    request: Request,
    incident_id: UUID,
    responder_id: UUID,
    body: ResponderUpdateRequest,
    responder_service: ResponderService = Depends(get_responder_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> ResponderResponse:
    await _get_incident_or_404(incident_id, incident_service)
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        responder = await responder_service.update_responder(responder_id, **fields)
    except ResponderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Responder not found"
        ) from e
    return ResponderResponse.from_domain(responder)


@router.delete("/{responder_id}", response_model=dict)
@limiter.limit("60/minute")
async def delete_responder(
    request: Request,
    incident_id: UUID,
    responder_id: UUID,
    responder_service: ResponderService = Depends(get_responder_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> dict[str, str]:
    await _get_incident_or_404(incident_id, incident_service)
    try:
        await responder_service.remove_responder(responder_id)
    except ResponderNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Responder not found"
        ) from e
    return {"detail": "Responder removed", "id": str(responder_id)}
