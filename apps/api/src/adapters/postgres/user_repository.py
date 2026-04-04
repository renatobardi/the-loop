"""PostgreSQL adapter implementing UserRepoPort."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserRow
from src.domain.exceptions import UserNotFoundError
from src.domain.models import User, UserPlan, _UnsetSentinel


def _row_to_domain(row: UserRow) -> User:
    """Convert database row to domain model."""
    return User(
        id=row.id,
        firebase_uid=row.firebase_uid,
        email=row.email,
        display_name=row.display_name,
        job_title=row.job_title,
        plan=UserPlan(row.plan),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PostgresUserRepository:
    """PostgreSQL implementation of user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(
        self, firebase_uid: str, email: str, display_name: str | None
    ) -> User:
        """Get existing user or create a new one (upsert by firebase_uid).

        display_name is only written on INSERT — not updated on subsequent calls.
        """
        stmt = select(UserRow).where(UserRow.firebase_uid == firebase_uid)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is not None:
            return _row_to_domain(row)

        user_id = uuid.uuid5(uuid.NAMESPACE_URL, f"firebase:{firebase_uid}")
        now = datetime.now(UTC)
        row = UserRow(
            id=user_id,
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            job_title=None,
            plan=UserPlan.BETA.value,
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        return _row_to_domain(row)

    async def update(
        self,
        user_id: UUID,
        display_name: str | None,
        job_title: str | None | _UnsetSentinel,
    ) -> User:
        """Update user profile fields.

        display_name: None = don't update; str = update to value.
        job_title: UNSET = don't update; None = clear to null; str = update to value.
        """
        row = await self._session.get(UserRow, user_id)
        if row is None:
            raise UserNotFoundError(str(user_id))

        if display_name is not None:
            row.display_name = display_name
        if not isinstance(job_title, _UnsetSentinel):
            row.job_title = job_title
        row.updated_at = datetime.now(UTC)

        await self._session.flush()
        await self._session.commit()
        return _row_to_domain(row)
