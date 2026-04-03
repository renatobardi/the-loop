"""Action item route handlers for incidents."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from starlette.requests import Request

from src.api.deps import get_action_item_service, get_authenticated_user, get_incident_service
from src.api.middleware import limiter
from src.domain.exceptions import ActionItemNotFoundError, IncidentNotFoundError
from src.domain.models import ActionItemPriority, ActionItemStatus, IncidentActionItem
from src.domain.services import ActionItemService, IncidentService

router = APIRouter(
    prefix="/api/v1/incidents/{incident_id}/action-items", tags=["action-items"]
)


class ActionItemCreateRequest(BaseModel):
    title: str
    description: str | None = None
    owner_id: UUID | None = None
    priority: ActionItemPriority = ActionItemPriority.MEDIUM
    due_date: date | None = None


class ActionItemUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    owner_id: UUID | None = None
    status: ActionItemStatus | None = None
    priority: ActionItemPriority | None = None
    due_date: date | None = None
    completed_by: UUID | None = None


class ActionItemResponse(BaseModel):
    id: UUID
    incident_id: UUID
    title: str
    description: str | None
    owner_id: UUID | None
    status: str
    priority: str
    due_date: str | None
    completed_at: str | None
    completed_by: UUID | None
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, item: IncidentActionItem) -> "ActionItemResponse":
        return cls(
            id=item.id,
            incident_id=item.incident_id,
            title=item.title,
            description=item.description,
            owner_id=item.owner_id,
            status=item.status.value,
            priority=item.priority.value,
            due_date=item.due_date.isoformat() if item.due_date else None,
            completed_at=item.completed_at.isoformat() if item.completed_at else None,
            completed_by=item.completed_by,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat(),
        )


class ActionItemListResponse(BaseModel):
    items: list[ActionItemResponse]
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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ActionItemResponse)
@limiter.limit("60/minute")
async def create_action_item(
    request: Request,
    incident_id: UUID,
    body: ActionItemCreateRequest,
    action_item_service: ActionItemService = Depends(get_action_item_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> ActionItemResponse:
    await _get_incident_or_404(incident_id, incident_service)
    item = await action_item_service.create_action_item(
        incident_id=incident_id,
        title=body.title,
        description=body.description,
        owner_id=body.owner_id,
        priority=body.priority,
        due_date=body.due_date,
    )
    return ActionItemResponse.from_domain(item)


@router.get("", response_model=ActionItemListResponse)
@limiter.limit("60/minute")
async def list_action_items(
    request: Request,
    incident_id: UUID,
    item_status: ActionItemStatus | None = Query(default=None, alias="status"),
    action_item_service: ActionItemService = Depends(get_action_item_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> ActionItemListResponse:
    await _get_incident_or_404(incident_id, incident_service)
    items = await action_item_service.list_action_items(incident_id, status=item_status)
    return ActionItemListResponse(
        items=[ActionItemResponse.from_domain(i) for i in items],
        total=len(items),
    )


@router.put("/{item_id}", response_model=ActionItemResponse)
@limiter.limit("60/minute")
async def update_action_item(
    request: Request,
    incident_id: UUID,
    item_id: UUID,
    body: ActionItemUpdateRequest,
    action_item_service: ActionItemService = Depends(get_action_item_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> ActionItemResponse:
    await _get_incident_or_404(incident_id, incident_service)
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        item = await action_item_service.update_action_item(item_id, **fields)
    except ActionItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Action item not found"
        ) from e
    return ActionItemResponse.from_domain(item)


@router.delete("/{item_id}", response_model=dict)
@limiter.limit("60/minute")
async def delete_action_item(
    request: Request,
    incident_id: UUID,
    item_id: UUID,
    action_item_service: ActionItemService = Depends(get_action_item_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> dict[str, str]:
    await _get_incident_or_404(incident_id, incident_service)
    try:
        await action_item_service.delete_action_item(item_id)
    except ActionItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Action item not found"
        ) from e
    return {"detail": "Action item deleted", "id": str(item_id)}
