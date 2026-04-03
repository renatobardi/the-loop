"""Timeline event route handlers for incidents."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from starlette.requests import Request

from src.api.deps import get_authenticated_user, get_incident_service, get_timeline_event_service
from src.api.middleware import limiter
from src.domain.exceptions import IncidentNotFoundError, TimelineEventNotFoundError
from src.domain.models import IncidentTimelineEvent, TimelineEventType
from src.domain.services import IncidentService, TimelineEventService

router = APIRouter(prefix="/api/v1/incidents/{incident_id}/timeline", tags=["timeline"])


class TimelineEventCreateRequest(BaseModel):
    event_type: TimelineEventType
    description: str
    occurred_at: datetime
    duration_minutes: int | None = None
    external_reference_url: str | None = None


class TimelineEventResponse(BaseModel):
    id: UUID
    incident_id: UUID
    event_type: str
    description: str
    occurred_at: str
    recorded_by: UUID
    duration_minutes: int | None
    external_reference_url: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, event: IncidentTimelineEvent) -> "TimelineEventResponse":
        return cls(
            id=event.id,
            incident_id=event.incident_id,
            event_type=event.event_type.value,
            description=event.description,
            occurred_at=event.occurred_at.isoformat(),
            recorded_by=event.recorded_by,
            duration_minutes=event.duration_minutes,
            external_reference_url=event.external_reference_url,
            created_at=event.created_at.isoformat(),
            updated_at=event.updated_at.isoformat(),
        )


class TimelineEventListResponse(BaseModel):
    items: list[TimelineEventResponse]
    total: int


async def _get_incident_or_404(incident_id: UUID, incident_service: IncidentService) -> None:
    try:
        await incident_service.get_by_id(incident_id)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        ) from e


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TimelineEventResponse)
@limiter.limit("60/minute")
async def create_timeline_event(
    request: Request,
    incident_id: UUID,
    body: TimelineEventCreateRequest,
    timeline_service: TimelineEventService = Depends(get_timeline_event_service),
    incident_service: IncidentService = Depends(get_incident_service),
    user_id: UUID = Depends(get_authenticated_user),
) -> TimelineEventResponse:
    await _get_incident_or_404(incident_id, incident_service)
    event = await timeline_service.create(
        incident_id=incident_id,
        event_type=body.event_type,
        description=body.description,
        occurred_at=body.occurred_at,
        recorded_by=user_id,
        duration_minutes=body.duration_minutes,
        external_reference_url=body.external_reference_url,
    )
    return TimelineEventResponse.from_domain(event)


@router.get("", response_model=TimelineEventListResponse)
@limiter.limit("60/minute")
async def list_timeline_events(
    request: Request,
    incident_id: UUID,
    timeline_service: TimelineEventService = Depends(get_timeline_event_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> TimelineEventListResponse:
    await _get_incident_or_404(incident_id, incident_service)
    events = await timeline_service.list_by_incident(incident_id)
    return TimelineEventListResponse(
        items=[TimelineEventResponse.from_domain(e) for e in events],
        total=len(events),
    )


@router.delete("/{event_id}", response_model=dict)
@limiter.limit("60/minute")
async def delete_timeline_event(
    request: Request,
    incident_id: UUID,
    event_id: UUID,
    timeline_service: TimelineEventService = Depends(get_timeline_event_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> dict[str, str]:
    await _get_incident_or_404(incident_id, incident_service)
    try:
        await timeline_service.delete(event_id)
    except TimelineEventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found"
        ) from e
    return {"detail": "Timeline event deleted", "id": str(event_id)}
