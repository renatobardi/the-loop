"""Integration tests for PostgresPostmortumRepository."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.postgres.postmortem_repository import PostgresPostmortumRepository
from src.domain.exceptions import PostmortumNotFoundError
from src.domain.models import Postmortem, PostmortumSeverity, RootCauseCategory


@pytest.fixture(autouse=True)
async def clean_postmortems(db_session: AsyncSession) -> None:
    """Truncate postmortems before each test — commit() means rollback alone is insufficient."""
    await db_session.execute(text("TRUNCATE TABLE postmortems CASCADE"))
    await db_session.commit()


@pytest.fixture
def repo(db_session: AsyncSession) -> PostgresPostmortumRepository:
    """Create a PostgresPostmortumRepository with a real database session."""
    return PostgresPostmortumRepository(db_session)


@pytest.fixture
def sample_postmortem() -> Postmortem:
    """Create a sample postmortem for testing."""
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
async def test_create_postmortem(
    repo: PostgresPostmortumRepository, sample_postmortem: Postmortem
) -> None:
    """Test creating a postmortem."""
    result = await repo.create(sample_postmortem)

    assert result.id == sample_postmortem.id
    assert result.incident_id == sample_postmortem.incident_id
    assert result.root_cause_category == RootCauseCategory.CODE_PATTERN
    assert result.description == sample_postmortem.description
    assert result.team_responsible == "backend"
    assert result.severity_for_rule == PostmortumSeverity.ERROR
    assert result.related_rule_id == "injection-001"
    assert not result.is_locked


@pytest.mark.asyncio
async def test_get_by_id_found(
    repo: PostgresPostmortumRepository, sample_postmortem: Postmortem
) -> None:
    """Test retrieving a postmortem by ID."""
    await repo.create(sample_postmortem)

    result = await repo.get_by_id(sample_postmortem.id)

    assert result.id == sample_postmortem.id
    assert result.incident_id == sample_postmortem.incident_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo: PostgresPostmortumRepository) -> None:
    """Test retrieving non-existent postmortem raises error."""
    postmortem_id = uuid4()

    with pytest.raises(PostmortumNotFoundError):
        await repo.get_by_id(postmortem_id)


@pytest.mark.asyncio
async def test_get_by_incident_id_found(
    repo: PostgresPostmortumRepository, sample_postmortem: Postmortem
) -> None:
    """Test retrieving a postmortem by incident ID."""
    await repo.create(sample_postmortem)

    result = await repo.get_by_incident_id(sample_postmortem.incident_id)

    assert result is not None
    assert result.incident_id == sample_postmortem.incident_id
    assert result.id == sample_postmortem.id


@pytest.mark.asyncio
async def test_get_by_incident_id_not_found(repo: PostgresPostmortumRepository) -> None:
    """Test retrieving postmortem for non-existent incident returns None."""
    incident_id = uuid4()

    result = await repo.get_by_incident_id(incident_id)

    assert result is None


@pytest.mark.asyncio
async def test_update_postmortem(
    repo: PostgresPostmortumRepository, sample_postmortem: Postmortem
) -> None:
    """Test updating a postmortem."""
    await repo.create(sample_postmortem)

    updated_postmortem = sample_postmortem.model_copy(
        update={
            "description": "Updated analysis with more details (20+ characters required).",
            "team_responsible": "security",
            "updated_at": datetime.now(UTC),
        }
    )
    result = await repo.update(updated_postmortem)

    assert result.id == sample_postmortem.id
    assert result.description == "Updated analysis with more details (20+ characters required)."
    assert result.team_responsible == "security"


@pytest.mark.asyncio
async def test_update_not_found(repo: PostgresPostmortumRepository) -> None:
    """Test updating non-existent postmortem raises error."""
    postmortem_id = uuid4()
    postmortem = Postmortem(
        id=postmortem_id,
        incident_id=uuid4(),
        root_cause_category=RootCauseCategory.INFRASTRUCTURE,
        description="Non-existent postmortem (20+ characters required).",
        team_responsible="ops",
        severity_for_rule=PostmortumSeverity.WARNING,
        created_by=uuid4(),
        created_at=datetime.now(UTC),
    )

    with pytest.raises(PostmortumNotFoundError):
        await repo.update(postmortem)


@pytest.mark.asyncio
async def test_delete_postmortem(
    repo: PostgresPostmortumRepository, sample_postmortem: Postmortem
) -> None:
    """Test deleting a postmortem."""
    await repo.create(sample_postmortem)

    await repo.delete(sample_postmortem.id)

    with pytest.raises(PostmortumNotFoundError):
        await repo.get_by_id(sample_postmortem.id)


@pytest.mark.asyncio
async def test_delete_not_found(repo: PostgresPostmortumRepository) -> None:
    """Test deleting non-existent postmortem raises error."""
    postmortem_id = uuid4()

    with pytest.raises(PostmortumNotFoundError):
        await repo.delete(postmortem_id)


@pytest.mark.asyncio
async def test_list_all_returns_multiple(
    repo: PostgresPostmortumRepository,
) -> None:
    """Test listing all postmortems."""
    incident_id_1 = uuid4()
    incident_id_2 = uuid4()

    postmortem_1 = Postmortem(
        id=uuid4(),
        incident_id=incident_id_1,
        root_cause_category=RootCauseCategory.CODE_PATTERN,
        description="First postmortem (20+ characters required minimum).",
        team_responsible="backend",
        severity_for_rule=PostmortumSeverity.ERROR,
        created_by=uuid4(),
        created_at=datetime.now(UTC),
    )

    postmortem_2 = Postmortem(
        id=uuid4(),
        incident_id=incident_id_2,
        root_cause_category=RootCauseCategory.INFRASTRUCTURE,
        description="Second postmortem (20+ characters required minimum).",
        team_responsible="ops",
        severity_for_rule=PostmortumSeverity.WARNING,
        created_by=uuid4(),
        created_at=datetime.now(UTC),
    )

    await repo.create(postmortem_1)
    await repo.create(postmortem_2)

    result = await repo.list_all()

    assert len(result) == 2
    assert result[0].id in [postmortem_1.id, postmortem_2.id]
    assert result[1].id in [postmortem_1.id, postmortem_2.id]


@pytest.mark.asyncio
async def test_list_all_empty(repo: PostgresPostmortumRepository) -> None:
    """Test listing all postmortems when none exist returns empty list."""
    result = await repo.list_all()

    assert result == []
