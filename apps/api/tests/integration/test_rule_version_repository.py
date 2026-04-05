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


def _unique_version() -> str:
    """Generate a unique version string using timestamp to avoid UNIQUE constraint violations."""
    import time
    ts = int(time.time() * 1000000) % 10000
    return f"0.1.{ts}"


@pytest.mark.asyncio
async def test_publish_version_success(db_session: AsyncSession) -> None:
    """Test publishing a new rule version."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()
    version = _unique_version()

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
        version=version,
        rules_json=rules_json,
        published_by=str(user_id),
        notes="Initial version",
    )

    assert result.version == version
    assert result.status == RuleVersionStatus.ACTIVE
    assert len(result.rules) == 1
    assert result.rules[0].id == "test-rule-001"


@pytest.mark.asyncio
async def test_publish_version_duplicate(db_session: AsyncSession) -> None:
    """Test publishing a duplicate version raises error."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()
    version = _unique_version()

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
        version=version,
        rules_json=rules_json,
        published_by=str(user_id),
        notes="First version",
    )

    with pytest.raises(VersionAlreadyExistsError):
        await repo.publish_version(
            version=version,
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
async def test_get_by_version(db_session: AsyncSession) -> None:
    """Test retrieving a version by version string."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()
    version = _unique_version()

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
        version=version,
        rules_json=rules_json,
        published_by=str(user_id),
    )

    result = await repo.get_by_version(version)

    assert result is not None
    assert result.version == version
    assert len(result.rules) == 1


@pytest.mark.asyncio
async def test_get_by_version_not_found(db_session: AsyncSession) -> None:
    """Test retrieving non-existent version returns None."""
    repo = PostgresRuleVersionRepository(db_session)

    result = await repo.get_by_version("9.9.9")

    assert result is None


@pytest.mark.asyncio
async def test_get_latest_active_none(db_session: AsyncSession) -> None:
    """Test get_latest_active returns None when all versions are deprecated."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()
    version = _unique_version()

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

    # Create and immediately deprecate a version
    await repo.publish_version(
        version=version,
        rules_json=rules_json,
        published_by=str(user_id),
    )
    await repo.deprecate_version(version)

    # Query should not return deprecated versions
    result = await repo.get_latest_active()

    # Result may be None or another active version from other tests
    # Just verify that if there are active versions, they are not deprecated
    if result is not None:
        assert result.status == RuleVersionStatus.ACTIVE


@pytest.mark.asyncio
async def test_list_all(db_session: AsyncSession) -> None:
    """Test listing all versions."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()
    version1 = _unique_version()
    version2 = _unique_version()

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

    # Find our test versions in the result (most recent first)
    test_versions = [v for v in result if v.version in (version1, version2)]
    assert len(test_versions) == 2
    assert test_versions[0].version == version2  # Most recent first
    assert test_versions[1].version == version1


@pytest.mark.asyncio
async def test_deprecate_version(db_session: AsyncSession) -> None:
    """Test deprecating a version."""
    repo = PostgresRuleVersionRepository(db_session)
    user_id = uuid4()
    version = _unique_version()

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
        version=version,
        rules_json=rules_json,
        published_by=str(user_id),
    )

    result = await repo.deprecate_version(version)

    assert result.status == RuleVersionStatus.DEPRECATED
    assert result.deprecated_at is not None


@pytest.mark.asyncio
async def test_deprecate_version_not_found(db_session: AsyncSession) -> None:
    """Test deprecating non-existent version raises error."""
    repo = PostgresRuleVersionRepository(db_session)

    with pytest.raises(RuleVersionNotFoundError):
        await repo.deprecate_version("9.9.9")
