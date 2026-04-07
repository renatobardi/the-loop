"""API-level tests for admin releases routes — sync from GitHub."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import FirebaseTokenData
from src.api.deps import require_admin
from src.api.routes.releases_admin import get_release_sync_service
from src.main import app

_ADMIN_ID = UUID("00000000-0000-0000-0000-000000000001")

_ADMIN_TOKEN: FirebaseTokenData = {
    "user_id": _ADMIN_ID,
    "firebase_uid": "firebase-admin-uid",
    "email": "admin@example.com",
    "display_name": "Admin",
}


@pytest.fixture
def mock_sync_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def admin_client(mock_sync_service: AsyncMock) -> AsyncClient:
    app.dependency_overrides[require_admin] = lambda: _ADMIN_TOKEN
    app.dependency_overrides[get_release_sync_service] = lambda: mock_sync_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def anon_client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_sync_releases_requires_admin(anon_client: AsyncClient) -> None:
    """POST /api/v1/admin/releases/sync requires admin auth."""
    response = await anon_client.post("/api/v1/admin/releases/sync")
    assert response.status_code in (401, 403)


async def test_sync_releases_success(
    admin_client: AsyncClient, mock_sync_service: AsyncMock
) -> None:
    """POST /api/v1/admin/releases/sync returns synced count on success."""
    mock_sync_service.sync_releases.return_value = 5
    response = await admin_client.post("/api/v1/admin/releases/sync")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["synced_count"] == 5


async def test_sync_releases_handles_error(
    admin_client: AsyncClient, mock_sync_service: AsyncMock
) -> None:
    """POST /api/v1/admin/releases/sync returns 500 on service error."""
    mock_sync_service.sync_releases.side_effect = RuntimeError("GitHub API down")
    response = await admin_client.post("/api/v1/admin/releases/sync")
    assert response.status_code == 500
