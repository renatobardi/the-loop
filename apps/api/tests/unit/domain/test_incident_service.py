"""Unit tests for IncidentService (postmortem validation)."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.domain.exceptions import (
    IncidentMissingPostmortumError,
)
from src.domain.models import Category, Incident, Severity
from src.domain.services import IncidentService

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_USER = uuid4()
_INCIDENT_ID = uuid4()


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


@pytest.fixture
def mock_incident_repo() -> MagicMock:
    """Create a mock IncidentRepository."""
    return MagicMock()


@pytest.fixture
def mock_postmortem_repo() -> MagicMock:
    """Create a mock PostmortumRepository."""
    return MagicMock()


@pytest.fixture
def service_with_postmortem_repo(
    mock_incident_repo: MagicMock, mock_postmortem_repo: MagicMock
) -> IncidentService:
    """Create an IncidentService with postmortem repo injected."""
    return IncidentService(mock_incident_repo, mock_postmortem_repo)


@pytest.mark.asyncio
class TestIncidentServicePostmortumValidation:
    """Tests for postmortem validation on incident update."""

    async def test_update_with_resolved_at_and_postmortem_exists(
        self,
        service_with_postmortem_repo: IncidentService,
        mock_incident_repo: MagicMock,
        mock_postmortem_repo: MagicMock,
    ) -> None:
        """Test update succeeds when resolved_at is set and postmortem exists."""
        incident = _make_incident()
        postmortem = MagicMock()  # Mock postmortem exists

        mock_incident_repo.get_by_id = AsyncMock(return_value=incident)
        mock_postmortem_repo.get_by_incident_id = AsyncMock(return_value=postmortem)
        updated_incident = incident.model_copy(
            update={"resolved_at": _NOW, "version": 2}
        )
        mock_incident_repo.update = AsyncMock(return_value=updated_incident)

        result = await service_with_postmortem_repo.update(
            _INCIDENT_ID, 1, resolved_at=_NOW
        )

        assert result.resolved_at == _NOW
        mock_postmortem_repo.get_by_incident_id.assert_called_once_with(_INCIDENT_ID)

    async def test_update_with_resolved_at_and_no_postmortem_raises_error(
        self,
        service_with_postmortem_repo: IncidentService,
        mock_incident_repo: MagicMock,
        mock_postmortem_repo: MagicMock,
    ) -> None:
        """Test update raises error when resolved_at is set but no postmortem exists."""
        incident = _make_incident()

        mock_incident_repo.get_by_id = AsyncMock(return_value=incident)
        mock_postmortem_repo.get_by_incident_id = AsyncMock(return_value=None)

        with pytest.raises(IncidentMissingPostmortumError):
            await service_with_postmortem_repo.update(
                _INCIDENT_ID, 1, resolved_at=_NOW
            )

        mock_postmortem_repo.get_by_incident_id.assert_called_once_with(_INCIDENT_ID)

    async def test_update_without_resolved_at_skips_postmortem_check(
        self,
        service_with_postmortem_repo: IncidentService,
        mock_incident_repo: MagicMock,
        mock_postmortem_repo: MagicMock,
    ) -> None:
        """Test update skips postmortem validation when resolved_at is not being changed."""
        incident = _make_incident()
        updated_incident = incident.model_copy(
            update={"impact_summary": "Database was down for 15 minutes", "version": 2}
        )

        mock_incident_repo.get_by_id = AsyncMock(return_value=incident)
        mock_incident_repo.update = AsyncMock(return_value=updated_incident)

        result = await service_with_postmortem_repo.update(
            _INCIDENT_ID, 1, impact_summary="Database was down for 15 minutes"
        )

        assert result.impact_summary == "Database was down for 15 minutes"
        # Postmortem check should not be called
        mock_postmortem_repo.get_by_incident_id.assert_not_called()

    async def test_update_without_postmortem_repo_skips_validation(
        self,
        mock_incident_repo: MagicMock,
    ) -> None:
        """Test update skips postmortem validation when postmortem repo not injected."""
        # Service without postmortem repo
        service = IncidentService(mock_incident_repo, None)
        incident = _make_incident()
        updated_incident = incident.model_copy(
            update={"resolved_at": _NOW, "version": 2}
        )

        mock_incident_repo.get_by_id = AsyncMock(return_value=incident)
        mock_incident_repo.update = AsyncMock(return_value=updated_incident)

        # Should not raise error even though postmortem check is skipped
        result = await service.update(_INCIDENT_ID, 1, resolved_at=_NOW)

        assert result.resolved_at == _NOW
