"""Unit tests for RuleVersionService."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from src.domain.exceptions import (
    InvalidVersionFormatError,
    RuleVersionNotFoundError,
    VersionAlreadyExistsError,
)
from src.domain.models import Rule, RuleVersion, RuleVersionStatus
from src.domain.services import RuleVersionService


@pytest.fixture
def mock_repository() -> MagicMock:
    """Create a mock RuleVersionRepository."""
    return MagicMock()


@pytest.fixture
def service(mock_repository: MagicMock) -> RuleVersionService:
    """Create a RuleVersionService with mocked repository."""
    return RuleVersionService(mock_repository)


@pytest.fixture
def sample_rule_version() -> RuleVersion:
    """Create a sample RuleVersion for testing."""
    return RuleVersion(
        id=uuid4(),
        version="0.1.0",
        rules=[
            Rule(
                id="injection-001",
                languages=["python"],
                message="SQL injection",
                severity="ERROR",
                metadata={"incident_id": "injection-001"},
                patterns=[],
            )
        ],
        status=RuleVersionStatus.ACTIVE,
        created_at=datetime.now(UTC),
        published_by=uuid4(),
    )


@pytest.mark.asyncio
class TestRuleVersionService:
    """Test RuleVersionService methods."""

    async def test_get_latest_active_found(
        self, service: RuleVersionService, sample_rule_version: RuleVersion
    ) -> None:
        """Test get_latest_active returns version when found."""
        service._repo.get_latest_active = AsyncMock(return_value=sample_rule_version)

        result = await service.get_latest_active()

        assert result == sample_rule_version
        service._repo.get_latest_active.assert_called_once()

    async def test_get_latest_active_not_found(self, service: RuleVersionService) -> None:
        """Test get_latest_active returns None when no active version exists."""
        service._repo.get_latest_active = AsyncMock(return_value=None)

        result = await service.get_latest_active()

        assert result is None
        service._repo.get_latest_active.assert_called_once()

    async def test_get_by_version_found(
        self, service: RuleVersionService, sample_rule_version: RuleVersion
    ) -> None:
        """Test get_by_version returns version when found."""
        service._repo.get_by_version = AsyncMock(return_value=sample_rule_version)

        result = await service.get_by_version("0.1.0")

        assert result == sample_rule_version
        service._repo.get_by_version.assert_called_once_with("0.1.0")

    async def test_get_by_version_not_found(self, service: RuleVersionService) -> None:
        """Test get_by_version returns None when not found."""
        service._repo.get_by_version = AsyncMock(return_value=None)

        result = await service.get_by_version("0.99.0")

        assert result is None
        service._repo.get_by_version.assert_called_once_with("0.99.0")

    async def test_list_all_returns_multiple(
        self, service: RuleVersionService, sample_rule_version: RuleVersion
    ) -> None:
        """Test list_all returns multiple versions."""
        versions = [sample_rule_version, sample_rule_version]
        service._repo.list_all = AsyncMock(return_value=versions)

        result = await service.list_all()

        assert len(result) == 2
        service._repo.list_all.assert_called_once()

    async def test_list_all_returns_empty(self, service: RuleVersionService) -> None:
        """Test list_all returns empty list when no versions exist."""
        service._repo.list_all = AsyncMock(return_value=[])

        result = await service.list_all()

        assert result == []
        service._repo.list_all.assert_called_once()

    async def test_publish_version_success(
        self, service: RuleVersionService, sample_rule_version: RuleVersion
    ) -> None:
        """Test publish_version creates new version."""
        service._repo.publish_version = AsyncMock(return_value=sample_rule_version)
        user_id = uuid4()
        rules_json = [
            {
                "id": "rule-1",
                "languages": ["python"],
                "message": "test",
                "severity": "ERROR",
                "metadata": {},
                "patterns": [],
            }
        ]

        result = await service.publish_version(
            "0.1.0", rules_json, user_id, "Release notes"
        )

        assert result == sample_rule_version
        service._repo.publish_version.assert_called_once_with(
            "0.1.0", rules_json, user_id, "Release notes"
        )

    async def test_publish_version_duplicate(self, service: RuleVersionService) -> None:
        """Test publish_version raises on duplicate version."""
        service._repo.publish_version = AsyncMock(
            side_effect=VersionAlreadyExistsError("0.1.0")
        )
        user_id = uuid4()

        with pytest.raises(VersionAlreadyExistsError):
            await service.publish_version("0.1.0", [], user_id)

    async def test_publish_version_invalid_semver(self, service: RuleVersionService) -> None:
        """Test publish_version raises on invalid semver."""
        service._repo.publish_version = AsyncMock(
            side_effect=InvalidVersionFormatError("invalid")
        )
        user_id = uuid4()

        with pytest.raises(InvalidVersionFormatError):
            await service.publish_version("invalid", [], user_id)

    async def test_deprecate_version_success(
        self, service: RuleVersionService, sample_rule_version: RuleVersion
    ) -> None:
        """Test deprecate_version updates status."""
        deprecated_version = RuleVersion(
            id=sample_rule_version.id,
            version=sample_rule_version.version,
            rules=sample_rule_version.rules,
            status=RuleVersionStatus.DEPRECATED,
            created_at=sample_rule_version.created_at,
            published_by=sample_rule_version.published_by,
            deprecated_at=datetime.now(UTC),
        )
        service._repo.deprecate_version = AsyncMock(return_value=deprecated_version)

        result = await service.deprecate_version("0.1.0")

        assert result.status == RuleVersionStatus.DEPRECATED
        assert result.deprecated_at is not None
        service._repo.deprecate_version.assert_called_once_with("0.1.0")

    async def test_deprecate_version_not_found(self, service: RuleVersionService) -> None:
        """Test deprecate_version raises when version not found."""
        service._repo.deprecate_version = AsyncMock(
            side_effect=RuleVersionNotFoundError("0.99.0")
        )

        with pytest.raises(RuleVersionNotFoundError):
            await service.deprecate_version("0.99.0")
