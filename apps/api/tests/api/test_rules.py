"""API-level tests for rule version routes — service and cache mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

from httpx import AsyncClient
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


async def test_get_latest_rules_from_cache(async_client: AsyncClient) -> None:
    """Test GET /rules/latest returns cached version when available."""
    # Override dependencies
    mock_cache = AsyncMock(spec=RuleVersionCache)
    mock_service = AsyncMock()
    cached_version = _make_rule_version(version="0.1.0", status=RuleVersionStatus.ACTIVE)
    mock_cache.get_latest = AsyncMock(return_value=cached_version)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.get("/api/v1/rules/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "0.1.0"
        assert data["status"] == "active"
        assert data["rules_count"] == 1
        assert response.headers["Cache-Control"] == "public, max-age=300"
    finally:
        app.dependency_overrides.clear()


async def test_get_latest_rules_from_service(async_client: AsyncClient) -> None:
    """Test GET /rules/latest fetches from service when cache miss."""
    mock_cache = AsyncMock(spec=RuleVersionCache)
    mock_service = AsyncMock()
    rule_version = _make_rule_version(version="0.2.0", status=RuleVersionStatus.ACTIVE)
    mock_cache.get_latest = AsyncMock(return_value=None)
    mock_cache.set_latest = AsyncMock()
    mock_service.get_latest_active = AsyncMock(return_value=rule_version)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.get("/api/v1/rules/latest")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "0.2.0"
    finally:
        app.dependency_overrides.clear()


async def test_get_latest_rules_not_found(async_client: AsyncClient) -> None:
    """Test GET /rules/latest returns 503 when no active version exists."""
    mock_cache = AsyncMock(spec=RuleVersionCache)
    mock_service = AsyncMock()
    mock_cache.get_latest = AsyncMock(return_value=None)
    mock_service.get_latest_active = AsyncMock(return_value=None)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.get("/api/v1/rules/latest")
        assert response.status_code == 503
    finally:
        app.dependency_overrides.clear()


async def test_get_rules_by_version(async_client: AsyncClient) -> None:
    """Test GET /rules/{version} returns specific version."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)
    rule_version = _make_rule_version(version="0.1.0")
    mock_service.get_by_version = AsyncMock(return_value=rule_version)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.get("/api/v1/rules/0.1.0")

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "0.1.0"
    finally:
        app.dependency_overrides.clear()


async def test_get_rules_by_version_not_found(async_client: AsyncClient) -> None:
    """Test GET /rules/{version} returns 404 when version not found."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)
    mock_service.get_by_version = AsyncMock(return_value=None)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.get("/api/v1/rules/9.9.9")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


async def test_list_all_versions(async_client: AsyncClient) -> None:
    """Test GET /rules/versions lists all versions."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)
    versions = [
        _make_rule_version(version="0.2.0", status=RuleVersionStatus.ACTIVE),
        _make_rule_version(version="0.1.0", status=RuleVersionStatus.DEPRECATED),
    ]
    mock_service.list_all = AsyncMock(return_value=versions)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.get("/api/v1/rules/versions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["versions"]) == 2
        assert data["versions"][0]["version"] == "0.2.0"
        assert data["versions"][0]["status"] == "active"
    finally:
        app.dependency_overrides.clear()


async def test_publish_rules_success(async_client: AsyncClient) -> None:
    """Test POST /rules/publish creates new version."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)
    new_version = _make_rule_version(version="0.2.0", status=RuleVersionStatus.DRAFT)
    mock_service.publish_version = AsyncMock(return_value=new_version)
    mock_cache.invalidate = AsyncMock()

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
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

        response = await async_client.post("/api/v1/rules/publish", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert "version" in data
        assert "rules_count" in data
        assert "created_at" in data
    finally:
        app.dependency_overrides.clear()


async def test_publish_rules_version_exists(async_client: AsyncClient) -> None:
    """Test POST /rules/publish returns 409 when version already exists."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)
    mock_service.publish_version = AsyncMock(
        side_effect=VersionAlreadyExistsError("0.1.0")
    )

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        payload = {
            "version": "0.1.0",
            "rules": [_make_rule().__dict__],
        }

        response = await async_client.post("/api/v1/rules/publish", json=payload)
        assert response.status_code == 409
    finally:
        app.dependency_overrides.clear()


async def test_publish_rules_invalid_format(async_client: AsyncClient) -> None:
    """Test POST /rules/publish returns 400 for invalid semver."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)
    mock_service.publish_version = AsyncMock(
        side_effect=InvalidVersionFormatError("invalid")
    )

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        payload = {
            "version": "invalid",
            "rules": [_make_rule().__dict__],
        }

        response = await async_client.post("/api/v1/rules/publish", json=payload)
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


async def test_publish_rules_missing_fields(async_client: AsyncClient) -> None:
    """Test POST /rules/publish returns 400 for missing required fields."""
    mock_service = AsyncMock()
    mock_cache = AsyncMock(spec=RuleVersionCache)

    app.dependency_overrides[get_rule_version_service] = lambda: mock_service
    app.dependency_overrides[get_rule_version_cache] = lambda: mock_cache

    try:
        response = await async_client.post("/api/v1/rules/publish", json={"version": "0.1.0"})
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()
