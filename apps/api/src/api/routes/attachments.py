"""Attachment route handlers for incidents."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from starlette.requests import Request

from src.api.deps import get_attachment_service, get_authenticated_user, get_incident_service
from src.api.middleware import limiter
from src.domain.exceptions import AttachmentNotFoundError, IncidentNotFoundError
from src.domain.models import AttachmentType, IncidentAttachment
from src.domain.services import AttachmentService, IncidentService

router = APIRouter(
    prefix="/api/v1/incidents/{incident_id}/attachments", tags=["attachments"]
)


class AttachmentRegisterRequest(BaseModel):
    uploaded_by: UUID | None = None
    filename: str
    mime_type: str
    file_size_bytes: int
    gcs_bucket: str
    gcs_object_path: str
    attachment_type: AttachmentType
    source_system: str | None = None
    source_url: str | None = None

    @field_validator("file_size_bytes")
    @classmethod
    def file_size_positive(cls, v: int) -> int:
        if v <= 0:
            msg = "file_size_bytes must be > 0"
            raise ValueError(msg)
        return v


class AttachmentResponse(BaseModel):
    id: UUID
    incident_id: UUID
    uploaded_by: UUID | None
    filename: str
    mime_type: str
    file_size_bytes: int
    gcs_bucket: str
    gcs_object_path: str
    content_text: str | None
    extraction_status: str
    attachment_type: str
    source_system: str | None
    source_url: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, a: IncidentAttachment) -> "AttachmentResponse":
        return cls(
            id=a.id,
            incident_id=a.incident_id,
            uploaded_by=a.uploaded_by,
            filename=a.filename,
            mime_type=a.mime_type,
            file_size_bytes=a.file_size_bytes,
            gcs_bucket=a.gcs_bucket,
            gcs_object_path=a.gcs_object_path,
            content_text=a.content_text,
            extraction_status=a.extraction_status.value,
            attachment_type=a.attachment_type.value,
            source_system=a.source_system,
            source_url=a.source_url,
            created_at=a.created_at.isoformat(),
            updated_at=a.updated_at.isoformat(),
        )


class AttachmentListResponse(BaseModel):
    items: list[AttachmentResponse]
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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AttachmentResponse)
@limiter.limit("60/minute")
async def register_attachment(
    request: Request,
    incident_id: UUID,
    body: AttachmentRegisterRequest,
    attachment_service: AttachmentService = Depends(get_attachment_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> AttachmentResponse:
    await _get_incident_or_404(incident_id, incident_service)
    attachment = await attachment_service.register_attachment(
        incident_id=incident_id,
        uploaded_by=body.uploaded_by,
        filename=body.filename,
        mime_type=body.mime_type,
        file_size_bytes=body.file_size_bytes,
        gcs_bucket=body.gcs_bucket,
        gcs_object_path=body.gcs_object_path,
        attachment_type=body.attachment_type,
        source_system=body.source_system,
        source_url=body.source_url,
    )
    return AttachmentResponse.from_domain(attachment)


@router.get("", response_model=AttachmentListResponse)
@limiter.limit("60/minute")
async def list_attachments(
    request: Request,
    incident_id: UUID,
    attachment_service: AttachmentService = Depends(get_attachment_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> AttachmentListResponse:
    await _get_incident_or_404(incident_id, incident_service)
    attachments = await attachment_service.list_attachments(incident_id)
    return AttachmentListResponse(
        items=[AttachmentResponse.from_domain(a) for a in attachments],
        total=len(attachments),
    )


@router.delete("/{attachment_id}", response_model=dict)
@limiter.limit("60/minute")
async def delete_attachment(
    request: Request,
    incident_id: UUID,
    attachment_id: UUID,
    attachment_service: AttachmentService = Depends(get_attachment_service),
    incident_service: IncidentService = Depends(get_incident_service),
    _user_id: UUID = Depends(get_authenticated_user),
) -> dict[str, str]:
    await _get_incident_or_404(incident_id, incident_service)
    try:
        await attachment_service.delete_attachment(attachment_id)
    except AttachmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        ) from e
    return {"detail": "Attachment deleted", "id": str(attachment_id)}
