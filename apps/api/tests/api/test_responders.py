"""API-level tests for responder routes — services mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_incident_service, get_responder_service
from src.domain.exceptions import DuplicateResponderError, IncidentNotFoundError
from src.domain.models import (
    Category,
    Incident,
    IncidentResponder,
    ResponderRole,
    Severity,
)
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_INCIDENT_ID = UUID("00000000-0000-0000-0000-000000000002")
_RESPONDER_ID = UUID("00000000-0000-0000-0000-000000000003")
_RESPONDER_USER = UUID("00000000-0000-0000-0000-000000000004")


def _make_incident() -> Incident:
    return Incident(
        id=_INCIDENT_ID,
        title="SQL injection",
        category=Category.INJECTION,
        severity=Severity.HIGH,
        anti_pattern="bad",
        remediation="fix",
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
        created_by=_USER,
    )


def _make_responder(**overrides: object) -> IncidentResponder:
    defaults: dict[str, object] = {
        "id": _RESPONDER_ID,
        "incident_id": _INCIDENT_ID,
        "user_id": _RESPONDER_USER,
        "role": ResponderRole.TECHNICAL_LEAD,
        "joined_at": _NOW,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return IncidentResponder(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_incident_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_responder_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(
    mock_incident_service: AsyncMock, mock_responder_service: AsyncMock
) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_incident_service] = lambda: mock_incident_service
    app.dependency_overrides[get_responder_service] = lambda: mock_responder_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


_ADD_BODY = {
    "user_id": str(_RESPONDER_USER),
    "role": "technical_lead",
}


async def test_add_responder(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_responder_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_responder_service.add_responder.return_value = _make_responder()

    resp = await client.post(f"/api/v1/incidents/{_INCIDENT_ID}/responders", json=_ADD_BODY)

    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "technical_lead"
    assert data["incident_id"] == str(_INCIDENT_ID)
    assert data["user_id"] == str(_RESPONDER_USER)


async def test_duplicate_responder_returns_409(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_responder_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_responder_service.add_responder.side_effect = DuplicateResponderError(
        str(_INCIDENT_ID), str(_RESPONDER_USER)
    )

    resp = await client.post(f"/api/v1/incidents/{_INCIDENT_ID}/responders", json=_ADD_BODY)

    assert resp.status_code == 409


async def test_list_responders_returns_items_total_envelope(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_responder_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_responder_service.list_responders.return_value = [
        _make_responder(),
        _make_responder(
            id=UUID("00000000-0000-0000-0000-000000000005"),
            user_id=UUID("00000000-0000-0000-0000-000000000006"),
            role=ResponderRole.INCIDENT_COMMANDER,
        ),
    ]

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/responders")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_update_responder_left_at(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_responder_service: AsyncMock,
) -> None:
    left_at = datetime(2025, 1, 2, tzinfo=UTC)
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_responder_service.update_responder.return_value = _make_responder(left_at=left_at)

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}/responders/{_RESPONDER_ID}",
        json={"left_at": left_at.isoformat()},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["left_at"] is not None


async def test_delete_responder(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_responder_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_responder_service.remove_responder.return_value = None

    resp = await client.delete(f"/api/v1/incidents/{_INCIDENT_ID}/responders/{_RESPONDER_ID}")

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Responder removed"


async def test_delete_incident_cascades_to_responders(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_responder_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/responders")
    assert resp.status_code == 404

    resp = await client.post(f"/api/v1/incidents/{_INCIDENT_ID}/responders", json=_ADD_BODY)
    assert resp.status_code == 404
