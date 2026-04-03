"""Unit tests for PostmortumService."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.domain.exceptions import (
    PostmortumAlreadyExistsError,
    PostmortumLockedError,
    PostmortumNotFoundError,
)
from src.domain.models import Postmortem, PostmortumSeverity, RootCauseCategory
from src.domain.services import PostmortumService


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create a mock PostmortumRepository."""
    return MagicMock()


@pytest.fixture
def service(mock_repository: MagicMock) -> PostmortumService:
    """Create a PostmortumService with mocked repository."""
    return PostmortumService(mock_repository)


@pytest.fixture
def sample_postmortem() -> Postmortem:
    """Create a sample Postmortem for testing."""
    return Postmortem(
        id=uuid4(),
        incident_id=uuid4(),
        root_cause_category=RootCauseCategory.CODE_PATTERN,
        description="SQL injection via string concatenation in user query handler.",
        suggested_pattern=r'execute\(".*"\s\+\s\w+\)',
        team_responsible="backend",
        severity_for_rule=PostmortumSeverity.ERROR,
        related_rule_id="injection-001",
        created_by=uuid4(),
        created_at=datetime.now(UTC),
        updated_by=None,
        updated_at=None,
        is_locked=False,
    )


@pytest.mark.asyncio
class TestPostmortumService:
    """Test PostmortumService methods."""

    async def test_create_success(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test create successfully creates a postmortem."""
        service._repo.get_by_incident_id = AsyncMock(return_value=None)
        service._repo.create = AsyncMock(return_value=sample_postmortem)

        result = await service.create(
            incident_id=sample_postmortem.incident_id,
            root_cause_category=RootCauseCategory.CODE_PATTERN,
            description="SQL injection via string concatenation in user query handler.",
            team_responsible="backend",
            severity_for_rule=PostmortumSeverity.ERROR,
            created_by=sample_postmortem.created_by,
            suggested_pattern=r'execute\(".*"\s\+\s\w+\)',
            related_rule_id="injection-001",
        )

        assert result.incident_id == sample_postmortem.incident_id
        assert result.root_cause_category == RootCauseCategory.CODE_PATTERN
        assert result.team_responsible == "backend"
        assert not result.is_locked
        service._repo.get_by_incident_id.assert_called_once_with(
            sample_postmortem.incident_id
        )
        service._repo.create.assert_called_once()

    async def test_create_already_exists(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test create raises error if postmortem already exists."""
        service._repo.get_by_incident_id = AsyncMock(return_value=sample_postmortem)

        with pytest.raises(PostmortumAlreadyExistsError):
            await service.create(
                incident_id=sample_postmortem.incident_id,
                root_cause_category=RootCauseCategory.CODE_PATTERN,
                description="SQL injection via string concatenation.",
                team_responsible="backend",
                severity_for_rule=PostmortumSeverity.ERROR,
                created_by=uuid4(),
            )

        service._repo.get_by_incident_id.assert_called_once()
        service._repo.create.assert_not_called()

    async def test_get_by_id_found(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test get_by_id returns postmortem when found."""
        service._repo.get_by_id = AsyncMock(return_value=sample_postmortem)

        result = await service.get_by_id(sample_postmortem.id)

        assert result == sample_postmortem
        service._repo.get_by_id.assert_called_once_with(sample_postmortem.id)

    async def test_get_by_id_not_found(self, service: PostmortumService) -> None:
        """Test get_by_id raises error when not found."""
        postmortem_id = uuid4()
        service._repo.get_by_id = AsyncMock(side_effect=PostmortumNotFoundError(postmortem_id))

        with pytest.raises(PostmortumNotFoundError):
            await service.get_by_id(postmortem_id)

    async def test_get_by_incident_id_found(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test get_by_incident_id returns postmortem when found."""
        service._repo.get_by_incident_id = AsyncMock(return_value=sample_postmortem)

        result = await service.get_by_incident_id(sample_postmortem.incident_id)

        assert result == sample_postmortem
        service._repo.get_by_incident_id.assert_called_once_with(
            sample_postmortem.incident_id
        )

    async def test_get_by_incident_id_not_found(self, service: PostmortumService) -> None:
        """Test get_by_incident_id returns None when not found."""
        incident_id = uuid4()
        service._repo.get_by_incident_id = AsyncMock(return_value=None)

        result = await service.get_by_incident_id(incident_id)

        assert result is None
        service._repo.get_by_incident_id.assert_called_once_with(incident_id)

    async def test_update_success(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test update successfully updates a postmortem."""
        service._repo.get_by_id = AsyncMock(return_value=sample_postmortem)
        updated_postmortem = sample_postmortem.model_copy(
            update={"description": "Updated description (20+ chars).", "updated_at": datetime.now(UTC)}
        )
        service._repo.update = AsyncMock(return_value=updated_postmortem)

        result = await service.update(
            sample_postmortem.id,
            description="Updated description (20+ chars).",
        )

        assert result.description == "Updated description (20+ chars)."
        service._repo.get_by_id.assert_called_once_with(sample_postmortem.id)
        service._repo.update.assert_called_once()

    async def test_update_locked_raises_error(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test update raises error if postmortem is locked."""
        locked_postmortem = sample_postmortem.model_copy(update={"is_locked": True})
        service._repo.get_by_id = AsyncMock(return_value=locked_postmortem)

        with pytest.raises(PostmortumLockedError):
            await service.update(
                locked_postmortem.id,
                description="Updated description (20+ chars).",
            )

        service._repo.get_by_id.assert_called_once()
        service._repo.update.assert_not_called()

    async def test_update_not_found(self, service: PostmortumService) -> None:
        """Test update raises error when postmortem not found."""
        postmortem_id = uuid4()
        service._repo.get_by_id = AsyncMock(side_effect=PostmortumNotFoundError(postmortem_id))

        with pytest.raises(PostmortumNotFoundError):
            await service.update(postmortem_id, description="New description (20+ chars).")

    async def test_lock_success(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test lock successfully locks a postmortem."""
        service._repo.get_by_id = AsyncMock(return_value=sample_postmortem)
        locked_postmortem = sample_postmortem.model_copy(
            update={"is_locked": True, "updated_at": datetime.now(UTC)}
        )
        service._repo.update = AsyncMock(return_value=locked_postmortem)

        result = await service.lock(sample_postmortem.id)

        assert result.is_locked
        service._repo.get_by_id.assert_called_once_with(sample_postmortem.id)
        service._repo.update.assert_called_once()

    async def test_lock_not_found(self, service: PostmortumService) -> None:
        """Test lock raises error when postmortem not found."""
        postmortem_id = uuid4()
        service._repo.get_by_id = AsyncMock(side_effect=PostmortumNotFoundError(postmortem_id))

        with pytest.raises(PostmortumNotFoundError):
            await service.lock(postmortem_id)

    async def test_list_all_returns_multiple(
        self, service: PostmortumService, sample_postmortem: Postmortem
    ) -> None:
        """Test list_all returns multiple postmortems."""
        postmortems = [sample_postmortem, sample_postmortem]
        service._repo.list_all = AsyncMock(return_value=postmortems)

        result = await service.list_all()

        assert result == postmortems
        assert len(result) == 2
        service._repo.list_all.assert_called_once()

    async def test_list_all_returns_empty(self, service: PostmortumService) -> None:
        """Test list_all returns empty list when no postmortems exist."""
        service._repo.list_all = AsyncMock(return_value=[])

        result = await service.list_all()

        assert result == []
        service._repo.list_all.assert_called_once()
