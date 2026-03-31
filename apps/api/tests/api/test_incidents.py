"""API-level tests for incident routes — service layer mocked via dependency override."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_incident_service
from src.domain.exceptions import (
    DuplicateSourceUrlError,
    IncidentHasActiveRuleError,
    IncidentNotFoundError,
    OptimisticLockError,
)
from src.domain.models import Category, Incident, Severity
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_INCIDENT_ID = UUID("00000000-0000-0000-0000-000000000002")


def _make_incident(**kwargs: object) -> Incident:
    defaults: dict[str, object] = {
        "id": _INCIDENT_ID,
        "title": "SQL injection via raw query",
        "category": Category.INJECTION,
        "severity": Severity.HIGH,
        "anti_pattern": "Raw SQL string interpolation",
        "remediation": "Use parameterised queries",
        "affected_languages": ["python"],
        "tags": [],
        "version": 1,
        "created_at": _NOW,
        "updated_at": _NOW,
        "created_by": _USER,
    }
    defaults.update(kwargs)
    return Incident(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(mock_service: AsyncMock) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_incident_service] = lambda: mock_service
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


_CREATE_BODY = {
    "title": "SQL injection via raw query",
    "category": "injection",
    "severity": "high",
    "anti_pattern": "Raw SQL string interpolation",
    "remediation": "Use parameterised queries",
}


async def test_create_incident_201(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.create.return_value = _make_incident()

    resp = await client.post("/api/v1/incidents", json=_CREATE_BODY)

    assert resp.status_code == 201
    assert resp.json()["title"] == "SQL injection via raw query"


async def test_create_incident_409_duplicate_url(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    mock_service.create.side_effect = DuplicateSourceUrlError("https://dup.com")

    resp = await client.post(
        "/api/v1/incidents",
        json={**_CREATE_BODY, "source_url": "https://dup.com"},
    )

    assert resp.status_code == 409
    assert "source_url" in resp.json()["detail"]


async def test_list_incidents_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_incidents.return_value = ([_make_incident()], 1)

    resp = await client.get("/api/v1/incidents")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


async def test_list_incidents_with_filters(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.list_incidents.return_value = ([], 0)

    resp = await client.get(
        "/api/v1/incidents",
        params={"category": "injection", "severity": "high", "q": "sql", "page": 2, "per_page": 10},
    )

    assert resp.status_code == 200
    call_kwargs = mock_service.list_incidents.call_args.kwargs
    assert call_kwargs["category"] == Category.INJECTION
    assert call_kwargs["keyword"] == "sql"


async def test_get_incident_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.get_by_id.return_value = _make_incident()

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}")

    assert resp.status_code == 200
    assert resp.json()["id"] == str(_INCIDENT_ID)


async def test_get_incident_404(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.get_by_id.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}")

    assert resp.status_code == 404


async def test_update_incident_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.update.return_value = _make_incident(title="Updated", version=2)

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}",
        json={"title": "Updated", "version": 1},
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


async def test_update_incident_404(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.update.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}", json={"version": 1}
    )

    assert resp.status_code == 404


async def test_update_incident_409_optimistic_lock(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    mock_service.update.side_effect = OptimisticLockError(str(_INCIDENT_ID), 2)

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}", json={"version": 1}
    )

    assert resp.status_code == 409
    assert "current_version" in resp.json()["detail"]


async def test_update_incident_409_active_rule(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    mock_service.update.side_effect = IncidentHasActiveRuleError(
        str(_INCIDENT_ID), "injection-001"
    )

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}",
        json={"category": "race-condition", "version": 1},
    )

    assert resp.status_code == 409


async def test_update_incident_409_duplicate_url(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    mock_service.update.side_effect = DuplicateSourceUrlError("https://dup.com")

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}",
        json={"source_url": "https://dup.com", "version": 1},
    )

    assert resp.status_code == 409


async def test_delete_incident_200(client: AsyncClient, mock_service: AsyncMock) -> None:
    resp = await client.delete(f"/api/v1/incidents/{_INCIDENT_ID}")

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Incident deleted"


async def test_delete_incident_404(client: AsyncClient, mock_service: AsyncMock) -> None:
    mock_service.soft_delete.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.delete(f"/api/v1/incidents/{_INCIDENT_ID}")

    assert resp.status_code == 404


async def test_delete_incident_409_active_rule(
    client: AsyncClient, mock_service: AsyncMock
) -> None:
    mock_service.soft_delete.side_effect = IncidentHasActiveRuleError(
        str(_INCIDENT_ID), "injection-001"
    )

    resp = await client.delete(f"/api/v1/incidents/{_INCIDENT_ID}")

    assert resp.status_code == 409
    assert "semgrep_rule_id" in resp.json()["detail"]
