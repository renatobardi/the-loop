"""Port definition for the Incident repository — Protocol-based structural subtyping."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import Category, Incident, Severity


class IncidentRepoPort(Protocol):
    async def create(self, incident: Incident) -> Incident: ...

    async def get_by_id(self, incident_id: UUID) -> Incident | None: ...

    async def update(self, incident: Incident, expected_version: int) -> Incident: ...

    async def soft_delete(self, incident_id: UUID) -> Incident | None: ...

    async def list_incidents(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        category: Category | None = None,
        severity: Severity | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Incident], int]:
        """Return (items, total_count)."""
        ...
