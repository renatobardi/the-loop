"""API-level tests for action item routes — services mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_action_item_service, get_incident_service
from src.domain.exceptions import IncidentNotFoundError
from src.domain.models import (
    ActionItemPriority,
    ActionItemStatus,
    Category,
    Incident,
    IncidentActionItem,
    Severity,
)
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_INCIDENT_ID = UUID("00000000-0000-0000-0000-000000000002")
_ITEM_ID = UUID("00000000-0000-0000-0000-000000000003")


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


def _make_item(**overrides: object) -> IncidentActionItem:
    defaults: dict[str, object] = {
        "id": _ITEM_ID,
        "incident_id": _INCIDENT_ID,
        "title": "Fix the bug",
        "status": ActionItemStatus.OPEN,
        "priority": ActionItemPriority.MEDIUM,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return IncidentActionItem(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_incident_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_action_item_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(
    mock_incident_service: AsyncMock, mock_action_item_service: AsyncMock
) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_incident_service] = lambda: mock_incident_service
    app.dependency_overrides[get_action_item_service] = lambda: mock_action_item_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


_CREATE_BODY = {"title": "Fix the bug"}


async def test_create_action_item(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_action_item_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_action_item_service.create_action_item.return_value = _make_item()

    resp = await client.post(f"/api/v1/incidents/{_INCIDENT_ID}/action-items", json=_CREATE_BODY)

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Fix the bug"
    assert data["status"] == "open"
    assert data["priority"] == "medium"
    assert data["completed_at"] is None


async def test_complete_action_item_sets_completed_at(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_action_item_service: AsyncMock,
) -> None:
    completed_at = datetime(2025, 1, 2, tzinfo=UTC)
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_action_item_service.update_action_item.return_value = _make_item(
        status=ActionItemStatus.COMPLETED,
        completed_at=completed_at,
        completed_by=_USER,
    )

    resp = await client.put(
        f"/api/v1/incidents/{_INCIDENT_ID}/action-items/{_ITEM_ID}",
        json={"status": "completed", "completed_by": str(_USER)},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


async def test_list_action_items_returns_items_total_envelope(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_action_item_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_action_item_service.list_action_items.return_value = [
        _make_item(),
        _make_item(
            id=UUID("00000000-0000-0000-0000-000000000004"),
            title="Write postmortem",
            priority=ActionItemPriority.HIGH,
        ),
    ]

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/action-items")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_list_action_items_filter_by_status(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_action_item_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_action_item_service.list_action_items.return_value = [_make_item()]

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/action-items?status=open")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    mock_action_item_service.list_action_items.assert_called_once_with(
        _INCIDENT_ID, status=ActionItemStatus.OPEN
    )


async def test_delete_action_item(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_action_item_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_action_item_service.delete_action_item.return_value = None

    resp = await client.delete(f"/api/v1/incidents/{_INCIDENT_ID}/action-items/{_ITEM_ID}")

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Action item deleted"


async def test_delete_incident_cascades_to_action_items(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_action_item_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/action-items")
    assert resp.status_code == 404

    resp = await client.post(f"/api/v1/incidents/{_INCIDENT_ID}/action-items", json=_CREATE_BODY)
    assert resp.status_code == 404
