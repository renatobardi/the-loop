"""Port interface for incident responder persistence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import IncidentResponder


class ResponderRepoPort(Protocol):
    async def create(self, responder: IncidentResponder) -> IncidentResponder: ...

    async def list_by_incident(self, incident_id: UUID) -> list[IncidentResponder]: ...

    async def get_by_id(self, responder_id: UUID) -> IncidentResponder | None: ...

    async def update(self, responder: IncidentResponder) -> IncidentResponder: ...

    async def delete(self, responder_id: UUID) -> None: ...
