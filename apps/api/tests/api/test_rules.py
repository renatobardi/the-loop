"""API-level tests for rule version routes — service and cache mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_rule_version_cache, get_rule_version_service, require_admin
from src.domain.exceptions import (
    InvalidVersionFormatError,
    VersionAlreadyExistsError,
)
from src.domain.models import Rule, RuleVersion, RuleVersionStatus
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_FAKE_ADMIN_TOKEN = {
    "user_id": _USER,
    "firebase_uid": "firebase-admin-uid",
    "email": "admin@example.com",
    "display_name": "Admin",
}


def _make_rule(**kwargs: object) -> Rule:
    defaults: dict[str, object] = {
        "id": "test-rule-001",
        "languages": ["python"],
        "message": "Test vulnerability detected",
        "severity": "ERROR",
        "metadata": {"cwe": "CWE-89", "category": "injection"},
        "patterns": [{"pattern": "test_pattern"}],
    }
    defaults.update(kwargs)
    return Rule(**defaults)  # type: ignore[arg-type]


def _make_rule_version(**kwargs: object) -> RuleVersion:
    defaults: dict[str, object] = {
        "id": UUID("00000000-0000-0000-0000-000000000003"),
        "version": "0.1.0",
        "rules": [_make_rule()],
        "status": RuleVersionStatus.ACTIVE,
        "created_at": _NOW,
        "published_by": _USER,
        "notes": None,
        "deprecated_at": None,
    }
    defaults.update(kwargs)
    return RuleVersion(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_rule_version_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_rule_version_cache() -> AsyncMock:
    return AsyncMock()


async def test_get_latest_rules_not_found(
    mock_rule_version_service: AsyncMock,
    mock_rule_version_cache: AsyncMock,
) -> None:
    """Test GET /rules/latest returns 503 when no active version exists."""
    mock_rule_version_cache.get_latest = AsyncMock(return_value=None)
    mock_rule_version_service.get_latest_active = AsyncMock(return_value=None)

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_rule_version_cache
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/rules/latest")
    app.dependency_overrides.clear()

    assert response.status_code == 503


async def test_get_latest_rules_cached_empty_rules_falls_through(
    mock_rule_version_service: AsyncMock,
    mock_rule_version_cache: AsyncMock,
) -> None:
    """Test GET /rules/latest falls through to DB when cached version has empty rules list.

    Regression test for: cache returning a RuleVersion with rules=[] would be treated
    as a cache hit and return 200 with empty rules. The fix ensures empty cached rules
    are treated as a cache miss, falling through to the DB fetch.
    """
    # Cache returns a RuleVersion with empty rules (stale/corrupt cache entry)
    empty_cached = _make_rule_version(rules=[])
    mock_rule_version_cache.get_latest = AsyncMock(return_value=empty_cached)

    # DB has the real active version with rules
    db_version = _make_rule_version(version="0.3.0", rules=[_make_rule()])
    mock_rule_version_service.get_latest_active = AsyncMock(return_value=db_version)
    mock_rule_version_cache.set_latest = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_rule_version_cache
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/rules/latest")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.3.0"
    assert len(data["rules"]) == 1
    # Must have fallen through to DB (not returned the empty cache)
    mock_rule_version_service.get_latest_active.assert_called_once()
    mock_rule_version_cache.set_latest.assert_called_once()


async def test_get_rules_by_version(mock_rule_version_service: AsyncMock) -> None:
    """Test GET /rules/{version} returns specific version."""
    rule_version = _make_rule_version(version="0.1.0")
    mock_rule_version_service.get_by_version = AsyncMock(return_value=rule_version)

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/rules/0.1.0")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"


async def test_get_rules_by_version_not_found(mock_rule_version_service: AsyncMock) -> None:
    """Test GET /rules/{version} returns 404 when version not found."""
    mock_rule_version_service.get_by_version = AsyncMock(return_value=None)

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/rules/9.9.9")
    app.dependency_overrides.clear()

    assert response.status_code == 404


async def test_list_all_versions(mock_rule_version_service: AsyncMock) -> None:
    """Test GET /rules/versions lists all versions."""
    versions = [
        _make_rule_version(version="0.2.0", status=RuleVersionStatus.ACTIVE),
        _make_rule_version(version="0.1.0", status=RuleVersionStatus.DEPRECATED),
    ]
    mock_rule_version_service.list_all = AsyncMock(return_value=versions)

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/rules/versions")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["versions"]) == 2
    assert data["versions"][0]["version"] == "0.2.0"
    assert data["versions"][0]["status"] == "active"


async def test_publish_rules_success(
    mock_rule_version_service: AsyncMock,
    mock_rule_version_cache: AsyncMock,
) -> None:
    """Test POST /rules/publish creates new version."""
    new_version = _make_rule_version(version="0.2.0", status=RuleVersionStatus.DRAFT)
    mock_rule_version_service.publish_version = AsyncMock(return_value=new_version)
    mock_rule_version_cache.invalidate = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_rule_version_cache
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "version": "0.2.0",
            "rules": [
                {
                    "id": "test-rule-001",
                    "languages": ["python"],
                    "message": "New rule",
                    "severity": "ERROR",
                    "metadata": {"cwe": "CWE-89"},
                    "patterns": [{"pattern": "test"}],
                }
            ],
            "notes": "Initial rules",
        }
        response = await ac.post("/api/v1/rules/publish", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert "version" in data
    assert "rules_count" in data
    assert "created_at" in data


async def test_publish_rules_version_exists(mock_rule_version_service: AsyncMock) -> None:
    """Test POST /rules/publish returns 409 when version already exists."""
    mock_rule_version_service.publish_version = AsyncMock(
        side_effect=VersionAlreadyExistsError("0.1.0")
    )

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "version": "0.1.0",
            "rules": [_make_rule().__dict__],
        }
        response = await ac.post("/api/v1/rules/publish", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 409


async def test_publish_rules_invalid_format(mock_rule_version_service: AsyncMock) -> None:
    """Test POST /rules/publish returns 400 for invalid semver."""
    mock_rule_version_service.publish_version = AsyncMock(
        side_effect=InvalidVersionFormatError("invalid")
    )

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "version": "invalid",
            "rules": [_make_rule().__dict__],
        }
        response = await ac.post("/api/v1/rules/publish", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 400


async def test_publish_rules_missing_fields() -> None:
    """Test POST /rules/publish returns 422 for missing required fields."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/publish", json={"version": "0.1.0"})
    app.dependency_overrides.clear()

    # 422 is correct — Pydantic validates request body before route handler
    assert response.status_code == 422


async def test_deprecate_version_success(
    mock_rule_version_service: AsyncMock,
    mock_rule_version_cache: AsyncMock,
) -> None:
    """Test POST /rules/deprecate marks version as deprecated."""
    deprecated_version = _make_rule_version(
        version="0.1.0", status=RuleVersionStatus.DEPRECATED, deprecated_at=_NOW
    )
    mock_rule_version_service.deprecate_version = AsyncMock(
        return_value=deprecated_version
    )
    mock_rule_version_cache.invalidate = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_rule_version_cache
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/deprecate", json={"version": "0.1.0"})
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"
    assert "deprecated_at" in data
    mock_rule_version_cache.invalidate.assert_called_once()


async def test_deprecate_version_not_found(mock_rule_version_service: AsyncMock) -> None:
    """Test POST /rules/deprecate returns 404 when version not found."""
    from src.domain.exceptions import RuleVersionNotFoundError

    mock_rule_version_service.deprecate_version = AsyncMock(
        side_effect=RuleVersionNotFoundError("0.99.0")
    )

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/deprecate", json={"version": "0.99.0"})
    app.dependency_overrides.clear()

    assert response.status_code == 404


async def test_deprecate_version_missing_auth() -> None:
    """Test POST /rules/deprecate returns 401 without auth token."""
    # No overrides — no auth header → 403 from require_admin (not authenticated)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/deprecate", json={"version": "0.1.0"})
    app.dependency_overrides.clear()

    assert response.status_code == 403


async def test_deprecate_version_invalid_semver() -> None:
    """Test POST /rules/deprecate returns 422 for invalid semver."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/deprecate", json={"version": "invalid"})
    app.dependency_overrides.clear()

    assert response.status_code == 422


async def test_list_deprecated_versions(mock_rule_version_service: AsyncMock) -> None:
    """Test GET /rules/deprecated returns only deprecated versions."""
    versions = [
        _make_rule_version(version="0.2.0", status=RuleVersionStatus.ACTIVE),
        _make_rule_version(
            version="0.1.0", status=RuleVersionStatus.DEPRECATED, deprecated_at=_NOW
        ),
    ]
    mock_rule_version_service.list_all = AsyncMock(return_value=versions)

    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/rules/deprecated")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["versions"]) == 1
    assert data["versions"][0]["version"] == "0.1.0"
    assert data["versions"][0]["status"] == "deprecated"
