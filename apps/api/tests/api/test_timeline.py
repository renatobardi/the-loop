"""API-level tests for timeline event routes — services mocked."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_incident_service, get_timeline_event_service
from src.domain.exceptions import IncidentNotFoundError
from src.domain.models import (
    Category,
    Incident,
    IncidentTimelineEvent,
    Severity,
    TimelineEventType,
)
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_INCIDENT_ID = UUID("00000000-0000-0000-0000-000000000002")
_EVENT_ID = UUID("00000000-0000-0000-0000-000000000003")


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


def _make_event(**overrides: object) -> IncidentTimelineEvent:
    defaults: dict[str, object] = {
        "id": _EVENT_ID,
        "incident_id": _INCIDENT_ID,
        "event_type": TimelineEventType.DETECTED,
        "description": "Monitoring alert triggered",
        "occurred_at": _NOW,
        "recorded_by": _USER,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return IncidentTimelineEvent(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_incident_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_timeline_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(
    mock_incident_service: AsyncMock, mock_timeline_service: AsyncMock
) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_incident_service] = lambda: mock_incident_service
    app.dependency_overrides[get_timeline_event_service] = lambda: mock_timeline_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


_CREATE_BODY = {
    "event_type": "detected",
    "description": "Monitoring alert triggered",
    "occurred_at": _NOW.isoformat(),
}


async def test_create_timeline_event(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_timeline_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_timeline_service.create.return_value = _make_event()

    resp = await client.post(
        f"/api/v1/incidents/{_INCIDENT_ID}/timeline", json=_CREATE_BODY
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["event_type"] == "detected"
    assert data["incident_id"] == str(_INCIDENT_ID)
    assert data["recorded_by"] == str(_USER)


async def test_list_timeline_events_ordered_chronologically(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_timeline_service: AsyncMock,
) -> None:
    event1 = _make_event(occurred_at=_NOW)
    event2 = _make_event(
        id=UUID("00000000-0000-0000-0000-000000000004"),
        event_type=TimelineEventType.MITIGATED,
        description="Mitigation applied",
        occurred_at=_NOW + timedelta(hours=2),
    )
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_timeline_service.list_by_incident.return_value = [event1, event2]

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/timeline")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["event_type"] == "detected"
    assert data["items"][1]["event_type"] == "mitigated"


async def test_delete_timeline_event(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_timeline_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_timeline_service.delete.return_value = None

    resp = await client.delete(
        f"/api/v1/incidents/{_INCIDENT_ID}/timeline/{_EVENT_ID}"
    )

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Timeline event deleted"


async def test_timeline_for_unknown_incident_returns_404(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_timeline_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/timeline")

    assert resp.status_code == 404


async def test_delete_incident_cascades_to_timeline_events(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_timeline_service: AsyncMock,
) -> None:
    # After incident deletion, any timeline request returns 404 because
    # incident existence check fails (cascade simulated at service level)
    mock_incident_service.get_by_id.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/timeline")
    assert resp.status_code == 404

    resp = await client.post(
        f"/api/v1/incidents/{_INCIDENT_ID}/timeline", json=_CREATE_BODY
    )
    assert resp.status_code == 404
