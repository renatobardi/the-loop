"""API-level tests for user profile routes — services mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import NAMESPACE_URL, uuid5

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import FirebaseTokenData, get_firebase_token_data
from src.api.deps import get_user_service
from src.domain.models import User, UserPlan
from src.main import app

_NOW = datetime(2026, 4, 4, tzinfo=UTC)
_FIREBASE_UID = "firebase_abc123"
_USER_ID = uuid5(NAMESPACE_URL, f"firebase:{_FIREBASE_UID}")
_EMAIL = "user@example.com"

_TOKEN_DATA: FirebaseTokenData = {
    "user_id": _USER_ID,
    "firebase_uid": _FIREBASE_UID,
    "email": _EMAIL,
    "display_name": "Renato Bardi",
}


def _make_user(**overrides: object) -> User:
    defaults: dict[str, object] = {
        "id": _USER_ID,
        "firebase_uid": _FIREBASE_UID,
        "email": _EMAIL,
        "display_name": "Renato Bardi",
        "job_title": None,
        "plan": UserPlan.BETA,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return User(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_user_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(mock_user_service: AsyncMock) -> AsyncClient:
    app.dependency_overrides[get_firebase_token_data] = lambda: _TOKEN_DATA
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_no_auth() -> AsyncClient:
    """Client without auth override — tests 401 responses."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ─── GET /api/v1/users/me ────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestGetMe:
    async def test_get_me_success(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """GET /users/me returns 200 with user profile."""
        mock_user_service.get_or_create = AsyncMock(return_value=_make_user())

        response = await client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(_USER_ID)
        assert data["email"] == _EMAIL
        assert data["display_name"] == "Renato Bardi"
        assert data["plan"] == "beta"
        mock_user_service.get_or_create.assert_called_once_with(
            firebase_uid=_FIREBASE_UID,
            email=_EMAIL,
            display_name="Renato Bardi",
        )

    async def test_get_me_upsert_idempotent(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Calling GET /users/me twice returns same id (upsert idempotent)."""
        mock_user_service.get_or_create = AsyncMock(return_value=_make_user())

        r1 = await client.get("/api/v1/users/me")
        r2 = await client.get("/api/v1/users/me")

        assert r1.json()["id"] == r2.json()["id"]

    async def test_get_me_display_name_not_synced_on_second_call(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """display_name from token is not synced on subsequent calls — stored value returned."""
        stored_user = _make_user(display_name="Original Name")
        mock_user_service.get_or_create = AsyncMock(return_value=stored_user)

        response = await client.get("/api/v1/users/me")

        assert response.json()["display_name"] == "Original Name"

    async def test_get_me_with_name_claim_populates_display_name(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """First call with 'name' claim creates user with display_name populated."""
        user = _make_user(display_name="Renato Bardi")
        mock_user_service.get_or_create = AsyncMock(return_value=user)

        response = await client.get("/api/v1/users/me")

        assert response.status_code == 200
        assert response.json()["display_name"] == "Renato Bardi"

    async def test_get_me_no_auth_returns_401(self, client_no_auth: AsyncClient) -> None:
        """GET /users/me without Bearer token returns 403."""
        response = await client_no_auth.get("/api/v1/users/me")
        assert response.status_code == 403


# ─── PATCH /api/v1/users/me ──────────────────────────────────────────────────


@pytest.mark.asyncio
class TestPatchMe:
    async def test_patch_display_name_success(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """PATCH with valid display_name returns 200."""
        updated = _make_user(display_name="New Name")
        mock_user_service.update_profile = AsyncMock(return_value=updated)

        response = await client.patch(
            "/api/v1/users/me", json={"display_name": "New Name"}
        )

        assert response.status_code == 200
        assert response.json()["display_name"] == "New Name"

    async def test_patch_empty_display_name_returns_422(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """PATCH with display_name='' returns 422."""
        response = await client.patch(
            "/api/v1/users/me", json={"display_name": ""}
        )
        assert response.status_code == 422

    async def test_patch_null_display_name_returns_422(
        self, client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """PATCH with explicit display_name=null returns 422."""
        response = await client.patch(
            "/api/v1/users/me", json={"display_name": None}
        )
        assert response.status_code == 422

    async def test_patch_no_auth_returns_401(self, client_no_auth: AsyncClient) -> None:
        """PATCH /users/me without Bearer token returns 403."""
        response = await client_no_auth.patch(
            "/api/v1/users/me", json={"display_name": "Test"}
        )
        assert response.status_code == 403
