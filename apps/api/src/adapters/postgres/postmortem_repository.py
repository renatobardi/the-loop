"""PostgreSQL adapter implementing PostmortumRepoPort."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import PostmortumRow
from src.domain.exceptions import PostmortumNotFoundError
from src.domain.models import Postmortem, PostmortumSeverity, RootCauseCategory


def _row_to_postmortem(row: PostmortumRow) -> Postmortem:
    """Convert database row to domain model."""
    return Postmortem(
        id=row.id,
        incident_id=row.incident_id,
        root_cause_category=RootCauseCategory(row.root_cause_category),
        description=row.description,
        suggested_pattern=row.suggested_pattern,
        team_responsible=row.team_responsible,
        severity_for_rule=PostmortumSeverity(row.severity_for_rule),
        related_rule_id=row.related_rule_id,
        created_by=row.created_by,
        created_at=row.created_at,
        updated_by=row.updated_by,
        updated_at=row.updated_at,
        is_locked=row.is_locked,
    )


class PostgresPostmortumRepository:
    """PostgreSQL implementation of postmortem repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, postmortem: Postmortem) -> Postmortem:
        """Create a new postmortem."""
        row = PostmortumRow(
            id=postmortem.id,
            incident_id=postmortem.incident_id,
            root_cause_category=postmortem.root_cause_category.value,
            description=postmortem.description,
            suggested_pattern=postmortem.suggested_pattern,
            team_responsible=postmortem.team_responsible,
            severity_for_rule=postmortem.severity_for_rule.value,
            related_rule_id=postmortem.related_rule_id,
            created_by=postmortem.created_by,
            created_at=postmortem.created_at,
            updated_by=postmortem.updated_by,
            updated_at=postmortem.updated_at,
            is_locked=postmortem.is_locked,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_postmortem(row)

    async def get_by_id(self, postmortem_id: UUID) -> Postmortem:
        """Retrieve postmortem by ID."""
        row = await self._session.get(PostmortumRow, postmortem_id)
        if row is None:
            raise PostmortumNotFoundError(postmortem_id)
        return _row_to_postmortem(row)

    async def get_by_incident_id(self, incident_id: UUID) -> Postmortem | None:
        """Retrieve postmortem by incident ID (1:1 relationship)."""
        stmt = select(PostmortumRow).where(PostmortumRow.incident_id == incident_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _row_to_postmortem(row) if row else None

    async def update(self, postmortem: Postmortem) -> Postmortem:
        """Update an existing postmortem."""
        row = await self._session.get(PostmortumRow, postmortem.id)
        if row is None:
            raise PostmortumNotFoundError(postmortem.id)

        row.root_cause_category = postmortem.root_cause_category.value
        row.description = postmortem.description
        row.suggested_pattern = postmortem.suggested_pattern
        row.team_responsible = postmortem.team_responsible
        row.severity_for_rule = postmortem.severity_for_rule.value
        row.related_rule_id = postmortem.related_rule_id
        row.updated_by = postmortem.updated_by
        row.updated_at = postmortem.updated_at
        row.is_locked = postmortem.is_locked

        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_postmortem(row)

    async def delete(self, postmortem_id: UUID) -> None:
        """Delete a postmortem."""
        row = await self._session.get(PostmortumRow, postmortem_id)
        if row is None:
            raise PostmortumNotFoundError(postmortem_id)
        await self._session.delete(row)
        await self._session.commit()

    async def list_all(self) -> list[Postmortem]:
        """List all postmortems ordered by created_at descending."""
        stmt = select(PostmortumRow).order_by(PostmortumRow.created_at.desc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [_row_to_postmortem(r) for r in rows]
