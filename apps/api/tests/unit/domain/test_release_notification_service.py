"""Unit tests for ReleaseNotificationService (Phase 5)."""

import pytest
from datetime import UTC, datetime
from uuid import uuid4

from src.domain.exceptions import ReleaseNotFoundError
from src.domain.models import Release, ReleaseNotificationStatus
from src.domain.services import ReleaseNotificationService


class MockReleaseRepository:
    def __init__(self, releases: dict):
        self.releases = releases

    async def get_all(self, limit: int = 10) -> list[Release]:
        return list(self.releases.values())[:limit]

    async def get_by_id(self, release_id) -> Release:
        if release_id not in self.releases:
            raise ReleaseNotFoundError(str(release_id))
        return self.releases[release_id]


class MockNotificationRepository:
    def __init__(self, statuses: dict):
        self.statuses = statuses

    async def get_by_user_and_release(self, user_id, release_id):
        key = (user_id, release_id)
        return self.statuses.get(key)

    async def get_unread_count(self, user_id) -> int:
        return sum(1 for (uid, _), status in self.statuses.items() if uid == user_id and not status.is_read)

    async def mark_as_read(self, user_id, release_id) -> ReleaseNotificationStatus:
        key = (user_id, release_id)
        status = ReleaseNotificationStatus(
            id=uuid4(),
            release_id=release_id,
            user_id=user_id,
            read_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
        self.statuses[key] = status
        return status


@pytest.fixture
def release1():
    return Release(
        id=uuid4(),
        title="v1.0.0",
        version="1.0.0",
        published_date=datetime(2026, 4, 5, tzinfo=UTC),
        summary="Initial release",
        changelog_html="<h1>Features</h1>",
        breaking_changes_flag=False,
        documentation_url="https://example.com/v1.0.0",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def release2():
    return Release(
        id=uuid4(),
        title="v1.1.0",
        version="1.1.0",
        published_date=datetime(2026, 4, 6, tzinfo=UTC),
        summary="Bug fixes",
        changelog_html="<h1>Fixes</h1>",
        breaking_changes_flag=False,
        documentation_url="https://example.com/v1.1.0",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def user_id():
    return uuid4()


@pytest.mark.asyncio
async def test_get_unread_count_returns_zero_when_all_read(release1, release2, user_id):
    """Test that get_unread_count returns 0 when all releases are marked read."""
    release_repo = MockReleaseRepository({release1.id: release1, release2.id: release2})
    status1 = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release1.id,
        user_id=user_id,
        read_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    status2 = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release2.id,
        user_id=user_id,
        read_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    notification_repo = MockNotificationRepository({(user_id, release1.id): status1, (user_id, release2.id): status2})

    service = ReleaseNotificationService(release_repo, notification_repo)
    count = await service.get_unread_count(user_id)

    assert count == 0


@pytest.mark.asyncio
async def test_get_unread_count_returns_correct_count(release1, release2, user_id):
    """Test that get_unread_count returns correct count of unread releases."""
    release_repo = MockReleaseRepository({release1.id: release1, release2.id: release2})
    status1 = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release1.id,
        user_id=user_id,
        read_at=None,  # Unread
        created_at=datetime.now(UTC),
    )
    status2 = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release2.id,
        user_id=user_id,
        read_at=datetime.now(UTC),  # Read
        created_at=datetime.now(UTC),
    )
    notification_repo = MockNotificationRepository({(user_id, release1.id): status1, (user_id, release2.id): status2})

    service = ReleaseNotificationService(release_repo, notification_repo)
    count = await service.get_unread_count(user_id)

    assert count == 1


@pytest.mark.asyncio
async def test_get_unread_releases_sorts_unread_first(release1, release2, user_id):
    """Test that unread releases are returned first, then by date descending."""
    release_repo = MockReleaseRepository({release1.id: release1, release2.id: release2})
    status1 = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release1.id,
        user_id=user_id,
        read_at=datetime.now(UTC),  # Read
        created_at=datetime.now(UTC),
    )
    status2 = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release2.id,
        user_id=user_id,
        read_at=None,  # Unread
        created_at=datetime.now(UTC),
    )
    notification_repo = MockNotificationRepository({(user_id, release1.id): status1, (user_id, release2.id): status2})

    service = ReleaseNotificationService(release_repo, notification_repo)
    results = await service.get_unread_releases(user_id, limit=10)

    # Unread (v1.1.0) should come first
    assert results[0][0].id == release2.id
    assert results[0][1] is False  # is_read = False
    assert results[1][0].id == release1.id
    assert results[1][1] is True  # is_read = True
