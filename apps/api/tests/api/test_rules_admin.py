"""API-level tests for admin rule routes — Phase 6."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_firebase_token_data
from src.api.deps import (
    get_rule_version_service,
    get_scan_service,
    get_user_service,
    require_admin,
)
from src.domain.exceptions import VersionAlreadyExistsError
from src.domain.models import Rule, RuleVersion, RuleVersionStatus
from src.main import app

_NOW = datetime(2026, 4, 4, tzinfo=UTC)
_ADMIN_ID = UUID("00000000-0000-0000-0000-000000000001")
_USER_ID = UUID("00000000-0000-0000-0000-000000000002")

_FAKE_ADMIN_TOKEN = {
    "user_id": _ADMIN_ID,
    "firebase_uid": "firebase-admin-uid",
    "email": "admin@example.com",
    "display_name": "Admin",
}

_FAKE_USER_TOKEN = {
    "user_id": _USER_ID,
    "firebase_uid": "firebase-user-uid",
    "email": "user@example.com",
    "display_name": "Regular User",
}


def _make_rule(**kwargs: object) -> Rule:
    defaults: dict[str, object] = {
        "id": "test-rule-001",
        "languages": ["python"],
        "message": "Test vulnerability detected",
        "severity": "ERROR",
        "metadata": {"cwe": "CWE-89"},
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
        "published_by": _ADMIN_ID,
        "notes": None,
        "deprecated_at": None,
    }
    defaults.update(kwargs)
    return RuleVersion(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_rule_version_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_scan_service() -> AsyncMock:
    return AsyncMock()


# ─── POST /api/v1/rules/versions ─────────────────────────────────────────────


async def test_create_rule_version_admin_success(
    mock_rule_version_service: AsyncMock,
) -> None:
    """Admin can create a draft version."""
    new_version = _make_rule_version(version="0.3.0", rules=[], status=RuleVersionStatus.ACTIVE)
    mock_rule_version_service.publish_version = AsyncMock(return_value=new_version)

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/versions", json={"version": "0.3.0"})
    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["version"] == "0.3.0"
    assert "status" in data


async def test_create_rule_version_non_admin_forbidden() -> None:
    """Non-admin users get 403."""
    from src.domain.models import User, UserPlan

    non_admin_user = User(
        id=_USER_ID,
        firebase_uid="firebase-user-uid",
        email="user@example.com",
        plan=UserPlan.BETA,
        is_admin=False,
        created_at=_NOW,
        updated_at=_NOW,
    )
    mock_user_service = AsyncMock()
    mock_user_service.get_or_create = AsyncMock(return_value=non_admin_user)

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_USER_TOKEN
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/rules/versions",
            json={"version": "0.3.0"},
            headers={"Authorization": "Bearer fake-token"},
        )
    app.dependency_overrides.clear()

    assert response.status_code == 403


async def test_create_rule_version_conflict(
    mock_rule_version_service: AsyncMock,
) -> None:
    """Returns 409 if version already exists."""
    mock_rule_version_service.publish_version = AsyncMock(
        side_effect=VersionAlreadyExistsError("0.1.0")
    )

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/rules/versions", json={"version": "0.1.0"})
    app.dependency_overrides.clear()

    assert response.status_code == 409


# ─── PUT /api/v1/rules/{version}/rules/{rule_id} ─────────────────────────────


async def test_edit_rule_admin_success(
    mock_rule_version_service: AsyncMock,
) -> None:
    """Admin can edit a rule in a version."""
    rule_version = _make_rule_version()
    mock_rule_version_service.get_by_version = AsyncMock(return_value=rule_version)

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service

    payload = {
        "message": "Updated message",
        "severity": "WARNING",
        "pattern": "new_pattern()",
        "languages": ["python"],
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put("/api/v1/rules/0.1.0/rules/test-rule-001", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


async def test_edit_rule_not_found_version(
    mock_rule_version_service: AsyncMock,
) -> None:
    """Returns 404 if version not found."""
    mock_rule_version_service.get_by_version = AsyncMock(return_value=None)

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_rule_version_service] = lambda: mock_rule_version_service

    payload = {
        "message": "msg",
        "severity": "ERROR",
        "pattern": "p",
        "languages": ["python"],
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put("/api/v1/rules/9.9.9/rules/test-rule-001", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 404


async def test_edit_rule_non_admin_forbidden() -> None:
    """Non-admin users get 403 on rule edit."""
    from src.domain.models import User, UserPlan

    non_admin_user = User(
        id=_USER_ID,
        firebase_uid="firebase-user-uid",
        email="user@example.com",
        plan=UserPlan.BETA,
        is_admin=False,
        created_at=_NOW,
        updated_at=_NOW,
    )
    mock_user_service = AsyncMock()
    mock_user_service.get_or_create = AsyncMock(return_value=non_admin_user)

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_USER_TOKEN
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    payload = {
        "message": "msg",
        "severity": "ERROR",
        "pattern": "p",
        "languages": ["python"],
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(
            "/api/v1/rules/0.1.0/rules/test-rule-001",
            json=payload,
            headers={"Authorization": "Bearer fake-token"},
        )
    app.dependency_overrides.clear()

    assert response.status_code == 403


# ─── GET /api/v1/admin/metrics ───────────────────────────────────────────────


async def test_get_admin_metrics_success(
    mock_scan_service: AsyncMock,
) -> None:
    """Admin can fetch global metrics."""
    mock_scan_service.get_global_metrics = AsyncMock(
        return_value={
            "active_repos": 5,
            "scans_by_week": [{"week": "2026-W14", "count": 3, "findings": 7}],
            "top_languages": [{"language": "Python", "count": 12}],
        }
    )

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[require_admin] = lambda: _FAKE_ADMIN_TOKEN
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/metrics")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["active_repos"] == 5
    assert "scans_by_week" in data
    assert "top_languages" in data


async def test_get_admin_metrics_non_admin_forbidden() -> None:
    """Non-admin users get 403 on metrics endpoint."""
    from src.domain.models import User, UserPlan

    non_admin_user = User(
        id=_USER_ID,
        firebase_uid="firebase-user-uid",
        email="user@example.com",
        plan=UserPlan.BETA,
        is_admin=False,
        created_at=_NOW,
        updated_at=_NOW,
    )
    mock_user_service = AsyncMock()
    mock_user_service.get_or_create = AsyncMock(return_value=non_admin_user)

    app.dependency_overrides[get_firebase_token_data] = lambda: _FAKE_USER_TOKEN
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/admin/metrics",
            headers={"Authorization": "Bearer fake-token"},
        )
    app.dependency_overrides.clear()

    assert response.status_code == 403
