"""Port interface for incident action item persistence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import ActionItemStatus, IncidentActionItem


class ActionItemRepoPort(Protocol):
    async def create(self, item: IncidentActionItem) -> IncidentActionItem: ...

    async def list_by_incident(
        self, incident_id: UUID, *, status_filter: ActionItemStatus | None = None
    ) -> list[IncidentActionItem]: ...

    async def get_by_id(self, item_id: UUID) -> IncidentActionItem | None: ...

    async def update(self, item: IncidentActionItem) -> IncidentActionItem: ...

    async def delete(self, item_id: UUID) -> None: ...
