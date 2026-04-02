"""Port interface for incident attachment persistence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import IncidentAttachment


class AttachmentRepoPort(Protocol):
    async def create(self, attachment: IncidentAttachment) -> IncidentAttachment: ...

    async def list_by_incident(self, incident_id: UUID) -> list[IncidentAttachment]: ...

    async def get_by_id(self, attachment_id: UUID) -> IncidentAttachment | None: ...

    async def delete(self, attachment_id: UUID) -> None: ...
