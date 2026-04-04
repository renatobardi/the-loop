"""API-level tests for scan routes — service layer mocked via dependency override."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import AsyncClient
from src.adapters.firebase.auth import get_firebase_token_data
from src.api.deps import ApiKeyContext, get_optional_identity, get_scan_service
from src.domain.models import ApiKey, Scan
from src.main import app

_NOW = datetime(2026, 4, 4, tzinfo=UTC)
_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
_KEY_ID = UUID("00000000-0000-0000-0000-000000000002")
_SCAN_ID = UUID("00000000-0000-0000-0000-000000000003")

_FAKE_TOKEN_DATA = {
    "user_id": _USER_ID,
    "firebase_uid": "firebase-uid-abc",
    "email": "test@example.com",
    "display_name": "Test User",
}

_FAKE_API_KEY = ApiKey(
    id=_KEY_ID,
    owner_id=_USER_ID,
    name="ci-key",
    prefix="tlp_abc",
    last_used_at=None,
    revoked_at=None,
    created_at=_NOW,
)

_FAKE_API_KEY_CONTEXT = ApiKeyContext(api_key=_FAKE_API_KEY, whitelist=[])


def _make_scan(**kwargs: object) -> Scan:
    defaults: dict[str, object] = {
        "id": _SCAN_ID,
        "api_key_id": _KEY_ID,
        "repository": "owner/repo",
        "branch": "main",
        "pr_number": None,
        "rules_version": "0.2.0",
        "findings_count": 2,
        "errors_count": 1,
        "warnings_count": 1,
        "duration_ms": 3500,
        "created_at": _NOW,
    }
    defaults.update(kwargs)
    return Scan(**defaults)  # type: ignore[arg-type]


_REGISTER_BODY = {
    "repository": "owner/repo",
    "branch": "main",
    "pr_number": None,
    "rules_version": "0.2.0",
    "findings_count": 2,
    "errors_count": 1,
    "warnings_count": 1,
    "duration_ms": 3500,
    "findings": [
        {
            "rule_id": "injection-001",
            "file_path": "app.py",
            "line_number": 42,
            "severity": "ERROR",
        }
    ],
}


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client_api_key(mock_service: AsyncMock) -> AsyncClient:
    """Client authenticated via API key context."""
    app.dependency_overrides[get_optional_identity] = lambda: _FAKE_API_KEY_CONTEXT
    app.dependency_overrides[get_scan_service] = lambda: mock_service
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_firebase(mock_service: AsyncMock) -> AsyncClient:
    """Client authenticated via Firebase token."""
    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_TOKEN_DATA
    app.dependency_overrides[get_scan_service] = lambda: mock_service
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_anonymous(mock_service: AsyncMock) -> AsyncClient:
    """Client with no authentication."""
    app.dependency_overrides[get_optional_identity] = lambda: None
    app.dependency_overrides[get_scan_service] = lambda: mock_service
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ─── POST /api/v1/scans ───────────────────────────────────────────────────────


async def test_register_scan_201(client_api_key: AsyncClient, mock_service: AsyncMock) -> None:
    scan = _make_scan()
    mock_service.register.return_value = scan

    resp = await client_api_key.post("/api/v1/scans", json=_REGISTER_BODY)

    assert resp.status_code == 201
    body = resp.json()
    assert body["repository"] == "owner/repo"
    assert body["findings_count"] == 2
    assert body["errors_count"] == 1


async def test_register_scan_401_no_api_key(
    client_anonymous: AsyncClient, mock_service: AsyncMock
) -> None:
    """POST /scans without API key context returns 401."""
    resp = await client_anonymous.post("/api/v1/scans", json=_REGISTER_BODY)

    assert resp.status_code == 401


async def test_register_scan_calls_service_with_api_key(
    client_api_key: AsyncClient, mock_service: AsyncMock
) -> None:
    scan = _make_scan()
    mock_service.register.return_value = scan

    await client_api_key.post("/api/v1/scans", json=_REGISTER_BODY)

    mock_service.register.assert_called_once()
    call_kwargs = mock_service.register.call_args.kwargs
    assert call_kwargs["api_key"] == _FAKE_API_KEY
    assert call_kwargs["repository"] == "owner/repo"
    assert call_kwargs["branch"] == "main"


async def test_register_scan_with_pr_number(
    client_api_key: AsyncClient, mock_service: AsyncMock
) -> None:
    scan = _make_scan(pr_number=99)
    mock_service.register.return_value = scan

    body = {**_REGISTER_BODY, "pr_number": 99}
    resp = await client_api_key.post("/api/v1/scans", json=body)

    assert resp.status_code == 201
    assert resp.json()["pr_number"] == 99


# ─── GET /api/v1/scans ────────────────────────────────────────────────────────


async def test_list_scans_200(client_firebase: AsyncClient, mock_service: AsyncMock) -> None:
    scans = [_make_scan()]
    mock_service.list_by_user.return_value = scans

    resp = await client_firebase.get("/api/v1/scans")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["repository"] == "owner/repo"


async def test_list_scans_empty(client_firebase: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_by_user.return_value = []

    resp = await client_firebase.get("/api/v1/scans")

    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["items"] == []


# ─── GET /api/v1/scans/summary ────────────────────────────────────────────────


async def test_get_scan_summary_200(client_firebase: AsyncClient, mock_service: AsyncMock) -> None:
    summary: dict[str, object] = {
        "total_scans": 5,
        "total_findings": 12,
        "scans_by_week": [{"week": "2026-W14", "count": 5, "findings": 12}],
        "top_rules": [{"rule_id": "injection-001", "count": 7}],
    }
    mock_service.get_summary.return_value = summary

    resp = await client_firebase.get("/api/v1/scans/summary")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total_scans"] == 5
    assert body["total_findings"] == 12
    assert len(body["scans_by_week"]) == 1
    assert len(body["top_rules"]) == 1


async def test_get_scan_summary_calls_service_with_owner(
    client_firebase: AsyncClient, mock_service: AsyncMock
) -> None:
    mock_service.get_summary.return_value = {
        "total_scans": 0,
        "total_findings": 0,
        "scans_by_week": [],
        "top_rules": [],
    }

    await client_firebase.get("/api/v1/scans/summary")

    mock_service.get_summary.assert_called_once_with(owner_id=_USER_ID)
