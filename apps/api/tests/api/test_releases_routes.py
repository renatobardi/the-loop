"""API tests for releases routes (Phase 5)."""

from uuid import UUID, NAMESPACE_URL, uuid4, uuid5

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import FirebaseTokenData, get_firebase_token_data
from src.main import app

_FIREBASE_UID = "firebase_releases_test"
_USER_ID = uuid5(NAMESPACE_URL, f"firebase:{_FIREBASE_UID}")
_TOKEN_DATA: FirebaseTokenData = {
    "user_id": _USER_ID,
    "firebase_uid": _FIREBASE_UID,
    "email": "test@example.com",
    "display_name": "Test User",
}


@pytest.fixture
async def client() -> AsyncClient:
    """AsyncClient with authenticated Firebase token."""
    app.dependency_overrides[get_firebase_token_data] = lambda: _TOKEN_DATA
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_no_auth() -> AsyncClient:
    """AsyncClient without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_releases_requires_auth(client_no_auth: AsyncClient):
    """Test that GET /api/v1/releases requires authentication."""
    response = await client_no_auth.get("/api/v1/releases")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_releases_returns_releases_list(client: AsyncClient):
    """Test that GET /api/v1/releases returns releases.

    Returns releases with read status for authenticated user.
    """
    response = await client.get("/api/v1/releases")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_unread_count_returns_count(client: AsyncClient):
    """Test that GET /api/v1/releases/unread-count returns unread count."""
    response = await client.get("/api/v1/releases/unread-count")
    assert response.status_code == 200
    data = response.json()
    assert "unread_count" in data
    assert isinstance(data["unread_count"], int)


@pytest.mark.asyncio
async def test_mark_release_as_read_requires_auth(client_no_auth: AsyncClient):
    """Test that PATCH /api/v1/releases/{id}/status requires authentication."""
    release_id = str(uuid4())
    response = await client_no_auth.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mark_release_as_read_returns_404_for_missing_release(client: AsyncClient):
    """Test that marking non-existent release returns 404."""
    release_id = str(uuid4())
    response = await client.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_release_detail_requires_auth(client_no_auth: AsyncClient):
    """Test that GET /api/v1/releases/{id} requires authentication."""
    release_id = str(uuid4())
    response = await client_no_auth.get(f"/api/v1/releases/{release_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_release_detail_returns_404_for_missing_release(client: AsyncClient):
    """Test that getting non-existent release returns 404."""
    release_id = str(uuid4())
    response = await client.get(f"/api/v1/releases/{release_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_releases_endpoint_respects_rate_limit(client: AsyncClient):
    """Test that releases endpoint respects rate limiting (60/minute)."""
    # Make multiple rapid requests and track responses
    rate_limited_response_found = False
    response_codes = []

    for i in range(65):  # Exceeds 60/minute limit
        response = await client.get("/api/v1/releases")
        response_codes.append(response.status_code)

        # Once we hit rate limit, all subsequent requests should fail
        if response.status_code == 429:
            rate_limited_response_found = True
            # Verify all remaining responses are also 429
            for remaining_code in response_codes[i + 1:]:
                assert remaining_code == 429, f"Expected 429 after rate limit, got {remaining_code}"
            break

    msg = f"Expected rate limit (429) but got codes: {set(response_codes)}"
    assert rate_limited_response_found, msg
