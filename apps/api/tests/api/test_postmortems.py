"""API-level tests for postmortem routes — services mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from src.adapters.firebase.auth import get_current_user
from src.api.deps import get_incident_service, get_postmortem_service
from src.domain.exceptions import (
    IncidentNotFoundError,
    PostmortumAlreadyExistsError,
    PostmortumLockedError,
    PostmortumNotFoundError,
)
from src.domain.models import (
    Category,
    Incident,
    Postmortem,
    PostmortumSeverity,
    RootCauseCategory,
    Severity,
)
from src.main import app

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = UUID("00000000-0000-0000-0000-000000000001")
_INCIDENT_ID = UUID("00000000-0000-0000-0000-000000000002")
_POSTMORTEM_ID = UUID("00000000-0000-0000-0000-000000000003")


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


def _make_postmortem(**overrides: object) -> Postmortem:
    defaults: dict[str, object] = {
        "id": _POSTMORTEM_ID,
        "incident_id": _INCIDENT_ID,
        "root_cause_category": RootCauseCategory.CODE_PATTERN,
        "description": "SQL injection via string concatenation (20+ chars minimum).",
        "team_responsible": "backend",
        "severity_for_rule": PostmortumSeverity.ERROR,
        "created_by": _USER,
        "created_at": _NOW,
        "is_locked": False,
    }
    defaults.update(overrides)
    return Postmortem(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_incident_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_postmortem_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(
    mock_incident_service: AsyncMock, mock_postmortem_service: AsyncMock
) -> AsyncClient:
    app.dependency_overrides[get_current_user] = lambda: _USER
    app.dependency_overrides[get_incident_service] = lambda: mock_incident_service
    app.dependency_overrides[get_postmortem_service] = lambda: mock_postmortem_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestCreatePostmortem:
    """Tests for POST /api/v1/incidents/{id}/postmortem."""

    async def test_create_success(
        self,
        client: AsyncClient,
        mock_incident_service: AsyncMock,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test creating a postmortem successfully."""
        mock_incident_service.get_by_id = AsyncMock(return_value=_make_incident())
        postmortem = _make_postmortem()
        mock_postmortem_service.create = AsyncMock(return_value=postmortem)

        response = await client.post(
            f"/api/v1/incidents/{_INCIDENT_ID}/postmortem",
            json={
                "root_cause_category": "code_pattern",
                "description": "SQL injection via string concatenation (20+ chars minimum).",
                "team_responsible": "backend",
                "severity_for_rule": "error",
                "suggested_pattern": r'execute\(".*"\s\+\s\w+\)',
                "related_rule_id": "injection-001",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(_POSTMORTEM_ID)
        assert data["incident_id"] == str(_INCIDENT_ID)
        assert data["team_responsible"] == "backend"

    async def test_create_incident_not_found(
        self,
        client: AsyncClient,
        mock_incident_service: AsyncMock,
    ) -> None:
        """Test creating postmortem for non-existent incident returns 404."""
        mock_incident_service.get_by_id = AsyncMock(
            side_effect=IncidentNotFoundError(str(_INCIDENT_ID))
        )

        response = await client.post(
            f"/api/v1/incidents/{_INCIDENT_ID}/postmortem",
            json={
                "root_cause_category": "code_pattern",
                "description": "SQL injection via string concatenation (20+ chars minimum).",
                "team_responsible": "backend",
                "severity_for_rule": "error",
            },
        )

        assert response.status_code == 404

    async def test_create_already_exists(
        self,
        client: AsyncClient,
        mock_incident_service: AsyncMock,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test creating duplicate postmortem returns 409 Conflict."""
        mock_incident_service.get_by_id = AsyncMock(return_value=_make_incident())
        mock_postmortem_service.create = AsyncMock(
            side_effect=PostmortumAlreadyExistsError(_INCIDENT_ID)
        )

        response = await client.post(
            f"/api/v1/incidents/{_INCIDENT_ID}/postmortem",
            json={
                "root_cause_category": "code_pattern",
                "description": "SQL injection via string concatenation (20+ chars minimum).",
                "team_responsible": "backend",
                "severity_for_rule": "error",
            },
        )

        assert response.status_code == 409


@pytest.mark.asyncio
class TestGetPostmortemByIncident:
    """Tests for GET /api/v1/incidents/{id}/postmortem."""

    async def test_get_by_incident_success(
        self,
        client: AsyncClient,
        mock_incident_service: AsyncMock,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test retrieving postmortem by incident ID."""
        mock_incident_service.get_by_id = AsyncMock(return_value=_make_incident())
        postmortem = _make_postmortem()
        mock_postmortem_service.get_by_incident_id = AsyncMock(return_value=postmortem)

        response = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/postmortem")

        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == str(_INCIDENT_ID)

    async def test_get_by_incident_not_found(
        self,
        client: AsyncClient,
        mock_incident_service: AsyncMock,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test retrieving postmortem when none exists returns 404."""
        mock_incident_service.get_by_id = AsyncMock(return_value=_make_incident())
        mock_postmortem_service.get_by_incident_id = AsyncMock(return_value=None)

        response = await client.get(f"/api/v1/incidents/{_INCIDENT_ID}/postmortem")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestGetPostmortem:
    """Tests for GET /api/v1/postmortems/{id}."""

    async def test_get_by_id_success(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test retrieving postmortem by ID."""
        postmortem = _make_postmortem()
        mock_postmortem_service.get_by_id = AsyncMock(return_value=postmortem)

        response = await client.get(f"/api/v1/postmortems/{_POSTMORTEM_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(_POSTMORTEM_ID)

    async def test_get_by_id_not_found(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test retrieving non-existent postmortem returns 404."""
        mock_postmortem_service.get_by_id = AsyncMock(
            side_effect=PostmortumNotFoundError(_POSTMORTEM_ID)
        )

        response = await client.get(f"/api/v1/postmortems/{_POSTMORTEM_ID}")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdatePostmortem:
    """Tests for PUT /api/v1/postmortems/{id}."""

    async def test_update_success(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test updating a postmortem."""
        original = _make_postmortem()
        updated = _make_postmortem(
            description="Updated analysis with more details (20+ characters required).",
            team_responsible="security",
        )
        mock_postmortem_service.get_by_id = AsyncMock(return_value=original)
        mock_postmortem_service.update = AsyncMock(return_value=updated)

        response = await client.put(
            f"/api/v1/postmortems/{_POSTMORTEM_ID}",
            json={
                "description": "Updated analysis with more details (20+ characters required).",
                "team_responsible": "security",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["team_responsible"] == "security"

    async def test_update_locked_returns_403(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test updating locked postmortem returns 403."""
        mock_postmortem_service.get_by_id = AsyncMock(return_value=_make_postmortem())
        mock_postmortem_service.update = AsyncMock(
            side_effect=PostmortumLockedError(_POSTMORTEM_ID)
        )

        response = await client.put(
            f"/api/v1/postmortems/{_POSTMORTEM_ID}",
            json={"description": "New description (20+ characters required minimum)."},
        )

        assert response.status_code == 403

    async def test_update_not_found(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test updating non-existent postmortem returns 404."""
        mock_postmortem_service.get_by_id = AsyncMock(
            side_effect=PostmortumNotFoundError(_POSTMORTEM_ID)
        )

        response = await client.put(
            f"/api/v1/postmortems/{_POSTMORTEM_ID}",
            json={"description": "New description (20+ characters required minimum)."},
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestLockPostmortem:
    """Tests for POST /api/v1/postmortems/{id}/lock."""

    async def test_lock_success(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test locking a postmortem."""
        original = _make_postmortem()
        locked = _make_postmortem(is_locked=True)
        mock_postmortem_service.get_by_id = AsyncMock(return_value=original)
        mock_postmortem_service.lock = AsyncMock(return_value=locked)

        response = await client.post(f"/api/v1/postmortems/{_POSTMORTEM_ID}/lock")

        assert response.status_code == 200
        data = response.json()
        assert data["is_locked"] is True

    async def test_lock_not_found(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test locking non-existent postmortem returns 404."""
        mock_postmortem_service.get_by_id = AsyncMock(
            side_effect=PostmortumNotFoundError(_POSTMORTEM_ID)
        )

        response = await client.post(f"/api/v1/postmortems/{_POSTMORTEM_ID}/lock")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestListTemplates:
    """Tests for GET /api/v1/postmortem-templates."""

    async def test_list_templates_success(self, client: AsyncClient) -> None:
        """Test listing postmortem templates."""
        response = await client.get("/api/v1/postmortem-templates")

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "count" in data
        assert data["count"] == len(data["templates"])
        # MVP includes 15 hardcoded templates
        assert data["count"] == 15
        # Check first template structure
        template = data["templates"][0]
        assert "id" in template
        assert "category" in template
        assert "title" in template
        assert "description_template" in template
        assert "severity_default" in template


@pytest.mark.asyncio
class TestListPostmortems:
    """Tests for GET /api/v1/postmortems (analytics listing)."""

    async def test_list_postmortems_success(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test listing all postmortems."""
        postmortem1 = _make_postmortem()
        postmortem2 = _make_postmortem(id=UUID("00000000-0000-0000-0000-000000000004"))
        mock_postmortem_service.list_all = AsyncMock(return_value=[postmortem1, postmortem2])

        response = await client.get("/api/v1/postmortems")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["items"]) == 2

    async def test_list_postmortems_empty(
        self,
        client: AsyncClient,
        mock_postmortem_service: AsyncMock,
    ) -> None:
        """Test listing postmortems when none exist returns empty list."""
        mock_postmortem_service.list_all = AsyncMock(return_value=[])

        response = await client.get("/api/v1/postmortems")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
