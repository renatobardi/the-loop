"""PostgreSQL adapter implementing AttachmentRepoPort."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import IncidentAttachmentRow
from src.domain.exceptions import AttachmentNotFoundError
from src.domain.models import AttachmentExtractionStatus, AttachmentType, IncidentAttachment


def _row_to_attachment(row: IncidentAttachmentRow) -> IncidentAttachment:
    return IncidentAttachment(
        id=row.id,
        incident_id=row.incident_id,
        uploaded_by=row.uploaded_by,
        filename=row.filename,
        mime_type=row.mime_type,
        file_size_bytes=row.file_size_bytes,
        gcs_bucket=row.gcs_bucket,
        gcs_object_path=row.gcs_object_path,
        content_text=row.content_text,
        extraction_status=AttachmentExtractionStatus(row.extraction_status),
        attachment_type=AttachmentType(row.attachment_type),
        source_system=row.source_system,
        source_url=row.source_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresAttachmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, attachment: IncidentAttachment) -> IncidentAttachment:
        row = IncidentAttachmentRow(
            id=attachment.id,
            incident_id=attachment.incident_id,
            uploaded_by=attachment.uploaded_by,
            filename=attachment.filename,
            mime_type=attachment.mime_type,
            file_size_bytes=attachment.file_size_bytes,
            gcs_bucket=attachment.gcs_bucket,
            gcs_object_path=attachment.gcs_object_path,
            content_text=attachment.content_text,
            extraction_status=attachment.extraction_status.value,
            attachment_type=attachment.attachment_type.value,
            source_system=attachment.source_system,
            source_url=attachment.source_url,
            created_at=attachment.created_at,
            updated_at=attachment.updated_at,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_attachment(row)

    async def list_by_incident(self, incident_id: UUID) -> list[IncidentAttachment]:
        stmt = select(IncidentAttachmentRow).where(IncidentAttachmentRow.incident_id == incident_id)
        result = await self._session.execute(stmt)
        return [_row_to_attachment(r) for r in result.scalars().all()]

    async def get_by_id(self, attachment_id: UUID) -> IncidentAttachment | None:
        row = await self._session.get(IncidentAttachmentRow, attachment_id)
        return _row_to_attachment(row) if row else None

    async def delete(self, attachment_id: UUID) -> None:
        row = await self._session.get(IncidentAttachmentRow, attachment_id)
        if row is None:
            raise AttachmentNotFoundError(str(attachment_id))
        await self._session.delete(row)
        await self._session.commit()
