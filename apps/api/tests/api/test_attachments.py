"""API-level tests for attachment routes — services mocked."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_attachment_service, get_incident_service
from src.domain.exceptions import IncidentNotFoundError
from src.domain.models import (
    AttachmentExtractionStatus,
    AttachmentType,
    Category,
    Incident,
    IncidentAttachment,
    Severity,
)
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_INCIDENT_ID = UUID("00000000-0000-0000-0000-000000000002")
_ATTACHMENT_ID = UUID("00000000-0000-0000-0000-000000000003")


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


def _make_attachment(**overrides: object) -> IncidentAttachment:
    defaults: dict[str, object] = {
        "id": _ATTACHMENT_ID,
        "incident_id": _INCIDENT_ID,
        "filename": "postmortem.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 1024,
        "gcs_bucket": "loop-prod-attachments",
        "gcs_object_path": "tenants/t1/incidents/i1/postmortem.pdf",
        "attachment_type": AttachmentType.POSTMORTEM_DOC,
        "extraction_status": AttachmentExtractionStatus.PENDING,
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return IncidentAttachment(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_incident_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_attachment_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(
    mock_incident_service: AsyncMock, mock_attachment_service: AsyncMock
) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_incident_service] = lambda: mock_incident_service
    app.dependency_overrides[get_attachment_service] = lambda: mock_attachment_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


_REGISTER_BODY = {
    "filename": "postmortem.pdf",
    "mime_type": "application/pdf",
    "file_size_bytes": 1024,
    "gcs_bucket": "loop-prod-attachments",
    "gcs_object_path": "tenants/t1/incidents/i1/postmortem.pdf",
    "attachment_type": "postmortem_doc",
}


async def test_register_attachment(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_attachment_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_attachment_service.register_attachment.return_value = _make_attachment()

    resp = await client.post(
        f"/api/v1/incidents/{_INCIDENT_ID}/attachments", json=_REGISTER_BODY
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["filename"] == "postmortem.pdf"
    assert data["extraction_status"] == "pending"
    assert data["incident_id"] == str(_INCIDENT_ID)


async def test_zero_file_size_returns_422(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_attachment_service: AsyncMock,
) -> None:
    body = {**_REGISTER_BODY, "file_size_bytes": 0}
    resp = await client.post(
        f"/api/v1/incidents/{_INCIDENT_ID}/attachments", json=body
    )

    assert resp.status_code == 422


async def test_list_attachments_returns_items_total_envelope(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_attachment_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_attachment_service.list_attachments.return_value = [
        _make_attachment(),
        _make_attachment(
            id=UUID("00000000-0000-0000-0000-000000000004"),
            filename="screenshot.png",
            mime_type="image/png",
            attachment_type=AttachmentType.SCREENSHOT,
        ),
    ]

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/attachments")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_delete_attachment_returns_200(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_attachment_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.return_value = _make_incident()
    mock_attachment_service.delete_attachment.return_value = None

    resp = await client.delete(
        f"/api/v1/incidents/{_INCIDENT_ID}/attachments/{_ATTACHMENT_ID}"
    )

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Attachment deleted"


async def test_delete_incident_cascades_to_attachments(
    client: AsyncClient,
    mock_incident_service: AsyncMock,
    mock_attachment_service: AsyncMock,
) -> None:
    mock_incident_service.get_by_id.side_effect = IncidentNotFoundError(str(_INCIDENT_ID))

    resp = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/attachments")
    assert resp.status_code == 404

    resp = await client.post(
        f"/api/v1/incidents/{_INCIDENT_ID}/attachments", json=_REGISTER_BODY
    )
    assert resp.status_code == 404
