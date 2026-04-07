"""End-to-end integration tests for Product Releases Notification (Phase 5).

These tests require a running PostgreSQL with migrations applied.
They verify the full stack: route → service → repository → database.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.postgres.notification_repository import (
    ReleaseNotificationStatusRepository,
)
from src.adapters.postgres.release_repository import ReleaseRepository
from src.domain.models import Release
from src.domain.services import ReleaseNotificationService

_USER = UUID("00000000-0000-0000-0000-000000000002")


async def test_release_notification_service_flow(db_session: AsyncSession) -> None:
    """Test service layer directly: create release → count unread → mark read → verify."""
    release_repo = ReleaseRepository(db_session)
    notification_repo = ReleaseNotificationStatusRepository(db_session)
    service = ReleaseNotificationService(release_repo, notification_repo)

    # 1. Create a test release
    release = Release(
        id=uuid4(),
        title="v1.0.0",
        version=f"1.0.0-{uuid4().hex[:8]}",
        published_date=datetime.now(UTC),
        summary="First release",
        changelog_html="<h1>Features</h1><p>Initial</p>",
        breaking_changes_flag=False,
        documentation_url="https://example.com/v1.0.0",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await release_repo.create(release)
    await db_session.commit()

    # 2. Count unread — should include the new release
    count = await service.get_unread_count(_USER)
    assert count >= 1

    # 3. Get releases with status
    results = await service.get_unread_releases(_USER, limit=10)
    assert len(results) >= 1

    # 4. Mark as read
    status = await service.mark_as_read(_USER, release.id)
    await db_session.commit()
    assert status.is_read is True

    # 5. Verify unread count decreased
    new_count = await service.get_unread_count(_USER)
    assert new_count < count
