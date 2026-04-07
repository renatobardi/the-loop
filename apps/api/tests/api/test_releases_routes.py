"""API tests for releases routes (Phase 5)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.routes.releases import get_release_service
from src.domain.exceptions import ReleaseNotFoundError
from src.main import app

_USER = UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(mock_service: AsyncMock) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_release_service] = lambda: mock_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_no_auth() -> AsyncClient:
    """Client without auth override — tests 401 responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_get_releases_requires_auth(client_no_auth: AsyncClient) -> None:
    """Test that GET /api/v1/releases requires authentication."""
    response = await client_no_auth.get("/api/v1/releases")
    assert response.status_code == 401


async def test_get_releases_returns_releases_list(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test that GET /api/v1/releases returns releases list."""
    mock_service.get_unread_releases.return_value = []
    response = await client.get("/api/v1/releases")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


async def test_get_unread_count_returns_count(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test that GET /api/v1/releases/unread-count returns unread count."""
    mock_service.get_unread_count.return_value = 3
    response = await client.get("/api/v1/releases/unread-count")
    assert response.status_code == 200
    data = response.json()
    assert "unread_count" in data
    assert data["unread_count"] == 3


async def test_mark_release_as_read_requires_auth(client_no_auth: AsyncClient) -> None:
    """Test that PATCH /api/v1/releases/{id}/status requires authentication."""
    release_id = str(uuid4())
    response = await client_no_auth.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 401


async def test_mark_release_as_read_returns_404_for_missing_release(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test that marking non-existent release returns 404."""
    release_id = uuid4()
    mock_service.mark_as_read.side_effect = ReleaseNotFoundError(str(release_id))
    response = await client.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 404


async def test_get_release_detail_requires_auth(client_no_auth: AsyncClient) -> None:
    """Test that GET /api/v1/releases/{id} requires authentication."""
    release_id = str(uuid4())
    response = await client_no_auth.get(f"/api/v1/releases/{release_id}")
    assert response.status_code == 401


async def test_get_release_detail_returns_404_for_missing_release(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test that getting non-existent release returns 404."""
    release_id = uuid4()
    mock_service.get_release_detail.side_effect = ReleaseNotFoundError(str(release_id))
    response = await client.get(f"/api/v1/releases/{release_id}")
    assert response.status_code == 404


async def test_get_releases_with_items(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test releases list with actual release items and status."""
    from datetime import UTC, datetime

    from src.domain.models import Release, ReleaseNotificationStatus

    release = Release(
        id=uuid4(),
        title="v1.0.0",
        version="1.0.0",
        published_date=datetime(2026, 4, 5, tzinfo=UTC),
        summary="Initial release",
        changelog_html="<h1>Features</h1>",
        breaking_changes_flag=False,
        documentation_url="https://example.com",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    status = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release.id,
        user_id=_USER,
        read_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    mock_service.get_unread_releases.return_value = [(release, status)]
    response = await client.get("/api/v1/releases")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["release"]["title"] == "v1.0.0"
    assert data["items"][0]["is_read"] is True


async def test_mark_release_as_read_success(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test successful mark-as-read returns notification status."""
    from datetime import UTC, datetime

    from src.domain.models import ReleaseNotificationStatus

    release_id = uuid4()
    status = ReleaseNotificationStatus(
        id=uuid4(),
        release_id=release_id,
        user_id=_USER,
        read_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    mock_service.mark_as_read.return_value = status
    response = await client.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["release_id"] == str(release_id)


async def test_get_release_detail_success(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test successful release detail returns full release data."""
    from datetime import UTC, datetime

    from src.domain.models import Release

    release_id = uuid4()
    release = Release(
        id=release_id,
        title="v2.0.0",
        version="2.0.0",
        published_date=datetime(2026, 4, 6, tzinfo=UTC),
        summary="Major update",
        changelog_html="<h1>Breaking</h1>",
        breaking_changes_flag=True,
        documentation_url="https://docs.example.com/v2",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.get_release_detail.return_value = release
    response = await client.get(f"/api/v1/releases/{release_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "v2.0.0"
    assert data["breaking_changes_flag"] is True


async def test_mark_release_as_read_handles_unexpected_error(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test mark-as-read returns 500 on unexpected service error."""
    release_id = uuid4()
    mock_service.mark_as_read.side_effect = RuntimeError("DB connection lost")
    response = await client.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 500


async def test_get_releases_with_unread_item(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test releases list with unread (no status) release."""
    from datetime import UTC, datetime

    from src.domain.models import Release

    release = Release(
        id=uuid4(),
        title="v1.1.0",
        version="1.1.0",
        published_date=datetime(2026, 4, 7, tzinfo=UTC),
        summary="Patch",
        changelog_html=None,
        breaking_changes_flag=False,
        documentation_url=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    mock_service.get_unread_releases.return_value = [(release, None)]
    response = await client.get("/api/v1/releases")
    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["is_read"] is False
    assert data["items"][0]["read_at"] is None


async def test_zz_releases_endpoint_respects_rate_limit(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test rate limiting (60/minute). Runs last (zz prefix) to avoid polluting other tests."""
    mock_service.get_unread_releases.return_value = []
    rate_limited = False
    for _ in range(65):
        response = await client.get("/api/v1/releases")
        if response.status_code == 429:
            rate_limited = True
            break
    assert rate_limited, "Expected 429 but never got rate limited"
