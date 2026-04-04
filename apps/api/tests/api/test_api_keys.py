"""API-level tests for api-key routes — service layer mocked via dependency override."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import AsyncClient
from src.adapters.firebase.auth import get_firebase_token_data
from src.api.deps import get_api_key_service
from src.domain.exceptions import ApiKeyNotFoundError
from src.domain.models import ApiKey
from src.main import app

_NOW = datetime(2026, 4, 4, tzinfo=UTC)
_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
_KEY_ID = UUID("00000000-0000-0000-0000-000000000002")

_FAKE_TOKEN_DATA = {
    "user_id": _USER_ID,
    "firebase_uid": "firebase-uid-abc",
    "email": "test@example.com",
    "display_name": "Test User",
}


def _make_api_key(**kwargs: object) -> ApiKey:
    defaults: dict[str, object] = {
        "id": _KEY_ID,
        "owner_id": _USER_ID,
        "name": "ci-key",
        "prefix": "tlp_abc",
        "last_used_at": None,
        "revoked_at": None,
        "created_at": _NOW,
    }
    defaults.update(kwargs)
    return ApiKey(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(mock_service: AsyncMock) -> AsyncClient:
    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_TOKEN_DATA
    app.dependency_overrides[get_api_key_service] = lambda: mock_service
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ─── POST /api/v1/api-keys ────────────────────────────────────────────────────


async def test_create_api_key_201(client: AsyncClient, mock_service: AsyncMock) -> None:
    api_key = _make_api_key()
    mock_service.create.return_value = ("tlp_abc1234567890", api_key)

    resp = await client.post("/api/v1/api-keys", json={"name": "ci-key"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "ci-key"
    assert body["prefix"] == "tlp_abc"
    assert "token" in body
    assert body["token"] == "tlp_abc1234567890"  # noqa: S105


async def test_create_api_key_calls_service_with_owner(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    api_key = _make_api_key()
    mock_service.create.return_value = ("tlp_token", api_key)

    await client.post("/api/v1/api-keys", json={"name": "my-key"})

    mock_service.create.assert_called_once()
    call_kwargs = mock_service.create.call_args.kwargs
    assert call_kwargs["owner_id"] == _USER_ID
    assert call_kwargs["name"] == "my-key"


# ─── GET /api/v1/api-keys ─────────────────────────────────────────────────────


async def test_list_api_keys_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    keys = [_make_api_key(), _make_api_key(id=UUID("00000000-0000-0000-0000-000000000003"))]
    mock_service.list_by_user.return_value = keys

    resp = await client.get("/api/v1/api-keys")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    # token hash must NOT be exposed
    for item in body:
        assert "token" not in item
        assert "key_hash" not in item


async def test_list_api_keys_empty(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_by_user.return_value = []

    resp = await client.get("/api/v1/api-keys")

    assert resp.status_code == 200
    assert resp.json() == []


# ─── DELETE /api/v1/api-keys/{id} ─────────────────────────────────────────────


async def test_revoke_api_key_204(client: AsyncClient, mock_service: AsyncMock) -> None:
    revoked = _make_api_key(revoked_at=_NOW)
    mock_service.revoke.return_value = revoked

    resp = await client.delete(f"/api/v1/api-keys/{_KEY_ID}")

    assert resp.status_code == 204


async def test_revoke_api_key_404(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.revoke.side_effect = ApiKeyNotFoundError(str(_KEY_ID))

    resp = await client.delete(f"/api/v1/api-keys/{_KEY_ID}")

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


# ─── GET /api/v1/api-keys/{id}/whitelist ──────────────────────────────────────


async def test_get_whitelist_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_by_user.return_value = [_make_api_key()]
    mock_service.get_whitelist.return_value = ["injection-001", "redos-001"]

    resp = await client.get(f"/api/v1/api-keys/{_KEY_ID}/whitelist")

    assert resp.status_code == 200
    assert resp.json()["rule_ids"] == ["injection-001", "redos-001"]


async def test_get_whitelist_404_wrong_owner(client: AsyncClient, mock_service: AsyncMock) -> None:
    # User doesn't own this key — list returns empty
    mock_service.list_by_user.return_value = []

    resp = await client.get(f"/api/v1/api-keys/{_KEY_ID}/whitelist")

    assert resp.status_code == 404


# ─── POST /api/v1/api-keys/{id}/whitelist ─────────────────────────────────────


async def test_add_to_whitelist_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_by_user.return_value = [_make_api_key()]
    mock_service.add_to_whitelist.return_value = None
    mock_service.get_whitelist.return_value = ["injection-001"]

    resp = await client.post(
        f"/api/v1/api-keys/{_KEY_ID}/whitelist",
        json={"rule_id": "injection-001"},
    )

    assert resp.status_code == 200
    assert "injection-001" in resp.json()["rule_ids"]


# ─── DELETE /api/v1/api-keys/{id}/whitelist/{rule_id} ─────────────────────────


async def test_remove_from_whitelist_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_by_user.return_value = [_make_api_key()]
    mock_service.remove_from_whitelist.return_value = None
    mock_service.get_whitelist.return_value = []

    resp = await client.delete(f"/api/v1/api-keys/{_KEY_ID}/whitelist/injection-001")

    assert resp.status_code == 200
    assert resp.json()["rule_ids"] == []
