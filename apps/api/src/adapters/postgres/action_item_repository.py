"""PostgreSQL adapter implementing ActionItemRepoPort."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import IncidentActionItemRow
from src.domain.exceptions import ActionItemNotFoundError
from src.domain.models import ActionItemPriority, ActionItemStatus, IncidentActionItem


def _row_to_action_item(row: IncidentActionItemRow) -> IncidentActionItem:
    return IncidentActionItem(
        id=row.id,
        incident_id=row.incident_id,
        title=row.title,
        description=row.description,
        owner_id=row.owner_id,
        status=ActionItemStatus(row.status),
        priority=ActionItemPriority(row.priority),
        due_date=row.due_date,
        completed_at=row.completed_at,
        completed_by=row.completed_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresActionItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, item: IncidentActionItem) -> IncidentActionItem:
        row = IncidentActionItemRow(
            id=item.id,
            incident_id=item.incident_id,
            title=item.title,
            description=item.description,
            owner_id=item.owner_id,
            status=item.status.value,
            priority=item.priority.value,
            due_date=item.due_date,
            completed_at=item.completed_at,
            completed_by=item.completed_by,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_action_item(row)

    async def list_by_incident(
        self,
        incident_id: UUID,
        *,
        status_filter: ActionItemStatus | None = None,
    ) -> list[IncidentActionItem]:
        stmt = select(IncidentActionItemRow).where(
            IncidentActionItemRow.incident_id == incident_id
        )
        if status_filter is not None:
            stmt = stmt.where(IncidentActionItemRow.status == status_filter.value)
        result = await self._session.execute(stmt)
        return [_row_to_action_item(r) for r in result.scalars().all()]

    async def get_by_id(self, item_id: UUID) -> IncidentActionItem | None:
        row = await self._session.get(IncidentActionItemRow, item_id)
        return _row_to_action_item(row) if row else None

    async def update(self, item: IncidentActionItem) -> IncidentActionItem:
        row = await self._session.get(IncidentActionItemRow, item.id)
        if row is None:
            raise ActionItemNotFoundError(str(item.id))
        row.title = item.title
        row.description = item.description
        row.owner_id = item.owner_id
        row.status = item.status.value
        row.priority = item.priority.value
        row.due_date = item.due_date
        row.completed_at = item.completed_at
        row.completed_by = item.completed_by
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_action_item(row)

    async def delete(self, item_id: UUID) -> None:
        row = await self._session.get(IncidentActionItemRow, item_id)
        if row is None:
            raise ActionItemNotFoundError(str(item_id))
        await self._session.delete(row)
        await self._session.commit()
