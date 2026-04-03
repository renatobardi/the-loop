"""PostgreSQL adapter implementing ResponderRepoPort."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import IncidentResponderRow
from src.domain.exceptions import DuplicateResponderError, ResponderNotFoundError
from src.domain.models import IncidentResponder, ResponderRole


def _row_to_responder(row: IncidentResponderRow) -> IncidentResponder:
    return IncidentResponder(
        id=row.id,
        incident_id=row.incident_id,
        user_id=row.user_id,
        role=ResponderRole(row.role),
        joined_at=row.joined_at,
        left_at=row.left_at,
        contribution_summary=row.contribution_summary,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresResponderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, responder: IncidentResponder) -> IncidentResponder:
        row = IncidentResponderRow(
            id=responder.id,
            incident_id=responder.incident_id,
            user_id=responder.user_id,
            role=responder.role.value,
            joined_at=responder.joined_at,
            left_at=responder.left_at,
            contribution_summary=responder.contribution_summary,
            created_at=responder.created_at,
            updated_at=responder.updated_at,
        )
        self._session.add(row)
        try:
            await self._session.flush()
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateResponderError(
                str(responder.incident_id), str(responder.user_id)
            ) from exc
        await self._session.refresh(row)
        return _row_to_responder(row)

    async def list_by_incident(self, incident_id: UUID) -> list[IncidentResponder]:
        stmt = select(IncidentResponderRow).where(IncidentResponderRow.incident_id == incident_id)
        result = await self._session.execute(stmt)
        return [_row_to_responder(r) for r in result.scalars().all()]

    async def get_by_id(self, responder_id: UUID) -> IncidentResponder | None:
        row = await self._session.get(IncidentResponderRow, responder_id)
        return _row_to_responder(row) if row else None

    async def update(self, responder: IncidentResponder) -> IncidentResponder:
        row = await self._session.get(IncidentResponderRow, responder.id)
        if row is None:
            raise ResponderNotFoundError(str(responder.id))
        row.role = responder.role.value
        row.left_at = responder.left_at
        row.contribution_summary = responder.contribution_summary
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_responder(row)

    async def delete(self, responder_id: UUID) -> None:
        row = await self._session.get(IncidentResponderRow, responder_id)
        if row is None:
            raise ResponderNotFoundError(str(responder_id))
        await self._session.delete(row)
        await self._session.commit()
