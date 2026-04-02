"""PostgreSQL adapter implementing TimelineEventRepoPort."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import IncidentTimelineEventRow
from src.domain.exceptions import TimelineEventNotFoundError
from src.domain.models import IncidentTimelineEvent, TimelineEventType


def _row_to_event(row: IncidentTimelineEventRow) -> IncidentTimelineEvent:
    return IncidentTimelineEvent(
        id=row.id,
        incident_id=row.incident_id,
        event_type=TimelineEventType(row.event_type),
        description=row.description,
        occurred_at=row.occurred_at,
        recorded_by=row.recorded_by,
        duration_minutes=row.duration_minutes,
        external_reference_url=row.external_reference_url,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresTimelineEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, event: IncidentTimelineEvent) -> IncidentTimelineEvent:
        row = IncidentTimelineEventRow(
            id=event.id,
            incident_id=event.incident_id,
            event_type=event.event_type.value,
            description=event.description,
            occurred_at=event.occurred_at,
            recorded_by=event.recorded_by,
            duration_minutes=event.duration_minutes,
            external_reference_url=event.external_reference_url,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_event(row)

    async def list_by_incident(
        self, incident_id: UUID, *, order_asc: bool = True
    ) -> list[IncidentTimelineEvent]:
        stmt = select(IncidentTimelineEventRow).where(
            IncidentTimelineEventRow.incident_id == incident_id
        )
        if order_asc:
            stmt = stmt.order_by(IncidentTimelineEventRow.occurred_at.asc())
        else:
            stmt = stmt.order_by(IncidentTimelineEventRow.occurred_at.desc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [_row_to_event(r) for r in rows]

    async def delete(self, event_id: UUID) -> None:
        row = await self._session.get(IncidentTimelineEventRow, event_id)
        if row is None:
            raise TimelineEventNotFoundError(str(event_id))
        await self._session.delete(row)
        await self._session.commit()
