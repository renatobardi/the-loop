"""Repository for ReleaseNotificationStatus CRUD operations (Phase 5 Product Releases Notification)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from src.adapters.postgres.models import ReleaseNotificationStatusRow
from src.domain.models import ReleaseNotificationStatus


class ReleaseNotificationStatusRepository:
    """Hexagonal repository for ReleaseNotificationStatus CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_and_release(
        self, user_id: UUID, release_id: UUID
    ) -> ReleaseNotificationStatus | None:
        """Fetch notification status for a user-release pair, return None if not found."""
        query = select(ReleaseNotificationStatusRow).where(
            and_(
                ReleaseNotificationStatusRow.user_id == user_id,
                ReleaseNotificationStatusRow.release_id == release_id,
            )
        )
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        return self._row_to_domain(row) if row else None

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread releases (read_at IS NULL) for user."""
        query = select(func.count()).select_from(ReleaseNotificationStatusRow).where(
            and_(
                ReleaseNotificationStatusRow.user_id == user_id,
                ReleaseNotificationStatusRow.read_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def mark_as_read(self, user_id: UUID, release_id: UUID) -> ReleaseNotificationStatus:
        """Mark release as read for user, creating notification status if needed."""
        # Try to get existing record
        status = await self.get_by_user_and_release(user_id, release_id)

        if status and status.is_read:
            # Already read, return as-is
            row = await self.session.get(ReleaseNotificationStatusRow, status.id)
            return self._row_to_domain(row) if row else status

        if status:
            # Unread, mark as read
            row = await self.session.get(ReleaseNotificationStatusRow, status.id)
            if row:
                row.read_at = datetime.now(UTC)
                await self.session.flush()
                return self._row_to_domain(row)
        else:
            # Create new notification status as read
            row = ReleaseNotificationStatusRow(
                user_id=user_id,
                release_id=release_id,
                read_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
            )
            self.session.add(row)
            await self.session.flush()
            return self._row_to_domain(row)

        # Fallback: re-fetch and return
        status = await self.get_by_user_and_release(user_id, release_id)
        return status or ReleaseNotificationStatus(
            id=UUID(int=0),
            release_id=release_id,
            user_id=user_id,
            read_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )

    async def get_recent_by_user(
        self, user_id: UUID, limit: int = 10
    ) -> list[ReleaseNotificationStatus]:
        """Get recent notifications for user, including both read and unread."""
        query = (
            select(ReleaseNotificationStatusRow)
            .where(ReleaseNotificationStatusRow.user_id == user_id)
            .order_by(ReleaseNotificationStatusRow.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [self._row_to_domain(row) for row in rows]

    async def create_or_get(
        self, user_id: UUID, release_id: UUID
    ) -> ReleaseNotificationStatus:
        """Create notification status if it doesn't exist, otherwise return existing."""
        existing = await self.get_by_user_and_release(user_id, release_id)
        if existing:
            return existing

        row = ReleaseNotificationStatusRow(
            user_id=user_id,
            release_id=release_id,
            read_at=None,
            created_at=datetime.now(UTC),
        )
        self.session.add(row)
        await self.session.flush()
        return self._row_to_domain(row)

    @staticmethod
    def _row_to_domain(row: ReleaseNotificationStatusRow) -> ReleaseNotificationStatus:
        """Convert ORM row to domain model."""
        return ReleaseNotificationStatus(
            id=row.id,
            release_id=row.release_id,
            user_id=row.user_id,
            read_at=row.read_at,
            created_at=row.created_at,
        )
