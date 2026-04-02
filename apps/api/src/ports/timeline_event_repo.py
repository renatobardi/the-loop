"""Port definition for the TimelineEvent repository."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import IncidentTimelineEvent


class TimelineEventRepoPort(Protocol):
    async def create(self, event: IncidentTimelineEvent) -> IncidentTimelineEvent: ...

    async def list_by_incident(
        self, incident_id: UUID, *, order_asc: bool = True
    ) -> list[IncidentTimelineEvent]: ...

    async def delete(self, event_id: UUID) -> None: ...
