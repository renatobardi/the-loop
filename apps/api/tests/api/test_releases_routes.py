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


async def test_releases_endpoint_respects_rate_limit(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test that releases endpoint respects rate limiting (60/minute)."""
    mock_service.get_unread_releases.return_value = []
    rate_limited = False
    for _ in range(65):
        response = await client.get("/api/v1/releases")
        if response.status_code == 429:
            rate_limited = True
            break
    assert rate_limited, f"Expected 429 but never got rate limited"
