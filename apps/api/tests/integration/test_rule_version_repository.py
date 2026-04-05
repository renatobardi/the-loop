"""Integration tests for PostgresRuleVersionRepository."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.postgres.rule_version_repository import PostgresRuleVersionRepository
from src.domain.exceptions import (
    InvalidVersionFormatError,
    RuleVersionNotFoundError,
    VersionAlreadyExistsError,
)
from src.domain.models import RuleVersionStatus


_version_counter = 0

@pytest.fixture
def test_version() -> str:
    """Provide unique version per test."""
    global _version_counter
    _version_counter += 1
    return f"0.{_version_counter}.0"


@pytest.mark.asyncio
async def test_publish_version_success(db_session: AsyncSession, test_version: str) -> None:
    """Test publishing a new rule version."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()

    rules_json = [
        {
            "id": "test-rule-001",
            "languages": ["python"],
            "message": "Test rule",
            "severity": "ERROR",
            "metadata": {"category": "test"},
            "patterns": [{"pattern": "test"}],
        }
    ]

    result = await repo.publish_version(
        version=test_version,
        rules_json=rules_json,
        published_by=str(user_id),
        notes="Initial version",
    )

    assert result.version == test_version
    assert result.status == RuleVersionStatus.ACTIVE
    assert len(result.rules) == 1
    assert result.rules[0].id == "test-rule-001"


@pytest.mark.asyncio
async def test_publish_version_duplicate(db_session: AsyncSession, test_version: str) -> None:
    """Test publishing a duplicate version raises error."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()

    rules_json = [
        {
            "id": "test-rule-001",
            "languages": ["python"],
            "message": "Test rule",
            "severity": "ERROR",
            "metadata": {"category": "test"},
            "patterns": [{"pattern": "test"}],
        }
    ]

    await repo.publish_version(
        version=test_version,
        rules_json=rules_json,
        published_by=str(user_id),
        notes="First version",
    )

    with pytest.raises(VersionAlreadyExistsError):
        await repo.publish_version(
            version=test_version,
            rules_json=rules_json,
            published_by=str(user_id),
            notes="Duplicate version",
        )


@pytest.mark.asyncio
async def test_publish_version_invalid_format(db_session: AsyncSession) -> None:
    """Test publishing with invalid semver format raises error."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()

    with pytest.raises(InvalidVersionFormatError):
        await repo.publish_version(
            version="invalid",
            rules_json=[],
            published_by=str(user_id),
        )


@pytest.mark.asyncio
async def test_get_by_version(db_session: AsyncSession, test_version: str) -> None:
    """Test retrieving a version by version string."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()

    rules_json = [
        {
            "id": "test-rule-001",
            "languages": ["python"],
            "message": "Test rule",
            "severity": "ERROR",
            "metadata": {"category": "test"},
            "patterns": [{"pattern": "test"}],
        }
    ]

    await repo.publish_version(
        version=test_version,
        rules_json=rules_json,
        published_by=str(user_id),
    )

    result = await repo.get_by_version(test_version)

    assert result is not None
    assert result.version == test_version
    assert len(result.rules) == 1


@pytest.mark.asyncio
async def test_get_by_version_not_found(db_session: AsyncSession) -> None:
    """Test retrieving non-existent version returns None."""
    repo = PostgresRuleVersionRepository(db_session)

    result = await repo.get_by_version("9.9.9")

    assert result is None


@pytest.mark.asyncio
async def test_get_latest_active_none(db_session: AsyncSession) -> None:
    """Test get_latest_active returns None when no active versions exist."""
    repo = PostgresRuleVersionRepository(db_session)

    result = await repo.get_latest_active()

    assert result is None


@pytest.mark.asyncio
async def test_list_all(db_session: AsyncSession, test_version: str) -> None:
    """Test listing all versions."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()

    rules_json = [
        {
            "id": "test-rule-001",
            "languages": ["python"],
            "message": "Test rule",
            "severity": "ERROR",
            "metadata": {"category": "test"},
            "patterns": [{"pattern": "test"}],
        }
    ]

    version1 = test_version
    version2 = f"0.{int(test_version.split('.')[1]) + 1}.0"

    await repo.publish_version(
        version=version1,
        rules_json=rules_json,
        published_by=str(user_id),
    )
    await repo.publish_version(
        version=version2,
        rules_json=rules_json,
        published_by=str(user_id),
    )

    result = await repo.list_all()

    assert len(result) == 2
    assert result[0].version == version2  # Most recent first
    assert result[1].version == version1


@pytest.mark.asyncio
async def test_deprecate_version(db_session: AsyncSession, test_version: str) -> None:
    """Test deprecating a version."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()

    rules_json = [
        {
            "id": "test-rule-001",
            "languages": ["python"],
            "message": "Test rule",
            "severity": "ERROR",
            "metadata": {"category": "test"},
            "patterns": [{"pattern": "test"}],
        }
    ]

    await repo.publish_version(
        version=test_version,
        rules_json=rules_json,
        published_by=str(user_id),
    )

    result = await repo.deprecate_version(test_version)

    assert result.status == RuleVersionStatus.DEPRECATED
    assert result.deprecated_at is not None


@pytest.mark.asyncio
async def test_deprecate_version_not_found(db_session: AsyncSession) -> None:
    """Test deprecating non-existent version raises error."""
    repo = PostgresRuleVersionRepository(db_session)

    with pytest.raises(RuleVersionNotFoundError):
        await repo.deprecate_version("9.9.9")
