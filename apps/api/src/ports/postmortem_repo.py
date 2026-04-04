"""Port definition for the Postmortem repository."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import Postmortem


class PostmortumRepoPort(Protocol):
    """Repository operations for postmortem root cause analysis."""

    async def create(self, postmortem: Postmortem) -> Postmortem:
        """Create a new postmortem for an incident."""
        ...

    async def get_by_id(self, postmortem_id: UUID) -> Postmortem:
        """Retrieve postmortem by ID. Raises PostmortumNotFoundError if not found."""
        ...

    async def get_by_incident_id(self, incident_id: UUID) -> Postmortem | None:
        """Retrieve postmortem by incident ID (1:1 relationship). Returns None if not exists."""
        ...

    async def update(self, postmortem: Postmortem) -> Postmortem:
        """Update an existing postmortem. Raises PostmortumNotFoundError if not found."""
        ...

    async def delete(self, postmortem_id: UUID) -> None:
        """Delete a postmortem. Raises PostmortumNotFoundError if not found."""
        ...

    async def list_all(self) -> list[Postmortem]:
        """List all postmortems for analytics and reporting. Ordered by created_at DESC."""
        ...
