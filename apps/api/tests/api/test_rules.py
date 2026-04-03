"""API-level tests for rule version routes — service and cache mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.adapters.postgres.cache import RuleVersionCache
from src.api.deps import get_rule_version_cache, get_rule_version_service
from src.domain.exceptions import (
    InvalidVersionFormatError,
    VersionAlreadyExistsError,
)
from src.domain.models import Rule, RuleVersion, RuleVersionStatus
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_cache() -> AsyncMock:
    cache = AsyncMock(spec=RuleVersionCache)
    cache.get_latest = AsyncMock(return_value=None)
    cache.set_latest = AsyncMock()
    cache.invalidate = AsyncMock()
    return cache


@pytest.fixture
async def client(mock_service: AsyncMock, mock_cache: AsyncMock) -> AsyncClient:
    """Create async client with mocked rule dependencies."""
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


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


async def test_get_latest_rules_from_cache(client: AsyncClient, mock_cache: AsyncMock) -> None:
    """Test GET /rules/latest returns cached version when available."""
    cached_version = _make_rule_version(version="0.1.0", status=RuleVersionStatus.ACTIVE)
    mock_cache.get_latest.return_value = cached_version

    response = await client.get("/api/v1/rules/latest")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"
    assert data["status"] == "active"
    assert data["rules_count"] == 1
    assert response.headers["Cache-Control"] == "public, max-age=300"


async def test_get_latest_rules_from_service(
    client: AsyncClient, mock_service: AsyncMock, mock_cache: AsyncMock
) -> None:
    """Test GET /rules/latest fetches from service when cache miss."""
    rule_version = _make_rule_version(version="0.2.0", status=RuleVersionStatus.ACTIVE)
    mock_cache.get_latest.return_value = None
    mock_service.get_latest_active.return_value = rule_version

    response = await client.get("/api/v1/rules/latest")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.2.0"


async def test_get_latest_rules_not_found(
    client: AsyncClient, mock_service: AsyncMock, mock_cache: AsyncMock
) -> None:
    """Test GET /rules/latest returns 503 when no active version exists."""
    mock_cache.get_latest.return_value = None
    mock_service.get_latest_active.return_value = None

    response = await client.get("/api/v1/rules/latest")

    assert response.status_code == 503


async def test_get_rules_by_version(client: AsyncClient, mock_service: AsyncMock) -> None:
    """Test GET /rules/{version} returns specific version."""
    rule_version = _make_rule_version(version="0.1.0")
    mock_service.get_by_version.return_value = rule_version

    response = await client.get("/api/v1/rules/0.1.0")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"


async def test_get_rules_by_version_not_found(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test GET /rules/{version} returns 404 when version not found."""
    mock_service.get_by_version.return_value = None

    response = await client.get("/api/v1/rules/9.9.9")

    assert response.status_code == 404


async def test_list_all_versions(client: AsyncClient, mock_service: AsyncMock) -> None:
    """Test GET /rules/versions lists all versions."""
    versions = [
        _make_rule_version(version="0.2.0", status=RuleVersionStatus.ACTIVE),
        _make_rule_version(version="0.1.0", status=RuleVersionStatus.DEPRECATED),
    ]
    mock_service.list_all.return_value = versions

    response = await client.get("/api/v1/rules/versions")

    assert response.status_code == 200
    data = response.json()
    assert len(data["versions"]) == 2
    assert data["versions"][0]["version"] == "0.2.0"
    assert data["versions"][0]["status"] == "active"


async def test_publish_rules_success(
    client: AsyncClient, mock_service: AsyncMock, mock_cache: AsyncMock
) -> None:
    """Test POST /rules/publish creates new version."""
    new_version = _make_rule_version(version="0.2.0", status=RuleVersionStatus.DRAFT)
    mock_service.publish_version.return_value = new_version

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

    response = await client.post("/api/v1/rules/publish", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "version" in data
    assert "rules_count" in data
    assert "created_at" in data


async def test_publish_rules_version_exists(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    """Test POST /rules/publish returns 409 when version already exists."""
    mock_service.publish_version.side_effect = VersionAlreadyExistsError("0.1.0")

    payload = {
        "version": "0.1.0",
        "rules": [_make_rule().__dict__],
    }

    response = await client.post("/api/v1/rules/publish", json=payload)

    assert response.status_code == 409


async def test_publish_rules_invalid_format(client: AsyncClient, mock_service: AsyncMock) -> None:
    """Test POST /rules/publish returns 400 for invalid semver."""
    mock_service.publish_version.side_effect = InvalidVersionFormatError("invalid")

    payload = {
        "version": "invalid",
        "rules": [_make_rule().__dict__],
    }

    response = await client.post("/api/v1/rules/publish", json=payload)

    assert response.status_code == 400


async def test_publish_rules_missing_fields(client: AsyncClient) -> None:
    """Test POST /rules/publish returns 400 for missing required fields."""
    response = await client.post("/api/v1/rules/publish", json={"version": "0.1.0"})

    assert response.status_code == 400
