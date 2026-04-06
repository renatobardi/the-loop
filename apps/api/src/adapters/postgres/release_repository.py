"""Repository for Release CRUD operations (Phase 5 Product Releases Notification)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc

from src.adapters.postgres.models import ReleaseRow
from src.domain.exceptions import ReleaseAlreadyExistsError, ReleaseNotFoundError
from src.domain.models import Release


class ReleaseRepository:
    """Hexagonal repository for Release CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, limit: int = 10) -> list[Release]:
        """Fetch recent releases ordered by published_date descending."""
        query = select(ReleaseRow).order_by(desc(ReleaseRow.published_date)).limit(limit)
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [self._row_to_domain(row) for row in rows]

    async def get_by_id(self, release_id: UUID) -> Release:
        """Fetch release by ID, raise ReleaseNotFoundError if not found."""
        query = select(ReleaseRow).where(ReleaseRow.id == release_id)
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        if not row:
            raise ReleaseNotFoundError(str(release_id))
        return self._row_to_domain(row)

    async def get_by_version(self, version: str) -> Release | None:
        """Fetch release by version, return None if not found."""
        query = select(ReleaseRow).where(ReleaseRow.version == version)
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        return self._row_to_domain(row) if row else None

    async def create(self, release: Release) -> Release:
        """Create new release, raise ReleaseAlreadyExistsError if version exists."""
        existing = await self.get_by_version(release.version)
        if existing:
            raise ReleaseAlreadyExistsError(release.version)

        row = ReleaseRow(
            id=release.id,
            title=release.title,
            version=release.version,
            published_date=release.published_date,
            summary=release.summary,
            changelog_html=release.changelog_html,
            breaking_changes_flag=release.breaking_changes_flag,
            documentation_url=release.documentation_url,
            created_at=release.created_at,
            updated_at=release.updated_at,
        )
        self.session.add(row)
        await self.session.flush()
        return self._row_to_domain(row)

    async def update(self, release_id: UUID, **kwargs: any) -> Release:
        """Update release fields, raise ReleaseNotFoundError if not found."""
        row = await self.session.get(ReleaseRow, release_id)
        if not row:
            raise ReleaseNotFoundError(str(release_id))

        for key, value in kwargs.items():
            if hasattr(row, key):
                setattr(row, key, value)

        row.updated_at = datetime.now(UTC)
        await self.session.flush()
        return self._row_to_domain(row)

    @staticmethod
    def _row_to_domain(row: ReleaseRow) -> Release:
        """Convert ORM row to domain model."""
        return Release(
            id=row.id,
            title=row.title,
            version=row.version,
            published_date=row.published_date,
            summary=row.summary,
            changelog_html=row.changelog_html,
            breaking_changes_flag=row.breaking_changes_flag,
            documentation_url=row.documentation_url,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
