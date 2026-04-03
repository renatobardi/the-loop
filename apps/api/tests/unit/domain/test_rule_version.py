"""Unit tests for Rule and RuleVersion domain models."""

import re
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.domain.models import Rule, RuleVersion, RuleVersionStatus


class TestRuleVersionStatus:
    """Test RuleVersionStatus enum."""

    def test_status_values(self) -> None:
        assert RuleVersionStatus.DRAFT.value == "draft"
        assert RuleVersionStatus.ACTIVE.value == "active"
        assert RuleVersionStatus.DEPRECATED.value == "deprecated"

    def test_status_enum_lookup(self) -> None:
        assert RuleVersionStatus("draft") == RuleVersionStatus.DRAFT
        assert RuleVersionStatus("active") == RuleVersionStatus.ACTIVE
        assert RuleVersionStatus("deprecated") == RuleVersionStatus.DEPRECATED

    def test_invalid_status(self) -> None:
        with pytest.raises(ValueError):
            RuleVersionStatus("invalid")


class TestRule:
    """Test Rule model (immutable)."""

    def test_rule_creation(self) -> None:
        rule = Rule(
            id="injection-001",
            languages=["python", "javascript"],
            message="SQL injection detected",
            severity="ERROR",
            metadata={"incident_id": "injection-001", "category": "injection"},
            patterns=[{"pattern": "concat($SQL, $VAR)"}],
        )
        assert rule.id == "injection-001"
        assert rule.languages == ["python", "javascript"]
        assert rule.severity == "ERROR"

    def test_rule_frozen(self) -> None:
        rule = Rule(
            id="injection-001",
            languages=["python"],
            message="test",
            severity="ERROR",
            metadata={},
            patterns=[],
        )
        with pytest.raises(Exception):  # FrozenModelError
            rule.id = "modified"  # type: ignore[misc]

    def test_rule_with_empty_patterns(self) -> None:
        rule = Rule(
            id="test",
            languages=["python"],
            message="test",
            severity="WARNING",
            metadata={},
            patterns=[],
        )
        assert rule.patterns == []


class TestRuleVersion:
    """Test RuleVersion model with validation."""

    def test_rule_version_creation(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()
        rules = [
            Rule(
                id="injection-001",
                languages=["python"],
                message="test",
                severity="ERROR",
                metadata={},
                patterns=[],
            )
        ]

        rv = RuleVersion(
            id=uuid4(),
            version="0.1.0",
            rules=rules,
            status=RuleVersionStatus.ACTIVE,
            created_at=now,
            published_by=user_id,
        )

        assert rv.version == "0.1.0"
        assert rv.status == RuleVersionStatus.ACTIVE
        assert rv.rules_count == 1

    def test_semver_validation_valid(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()

        valid_versions = ["0.1.0", "1.0.0", "0.2.15", "10.20.30"]
        for version in valid_versions:
            rv = RuleVersion(
                id=uuid4(),
                version=version,
                rules=[],
                status=RuleVersionStatus.DRAFT,
                created_at=now,
                published_by=user_id,
            )
            assert rv.version == version

    def test_semver_validation_invalid(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()

        invalid_versions = ["0.1", "v0.1.0", "0.1.0.0", "0.1.a", "0.1.-1"]
        for version in invalid_versions:
            with pytest.raises(ValueError, match="Invalid semantic version"):
                RuleVersion(
                    id=uuid4(),
                    version=version,
                    rules=[],
                    status=RuleVersionStatus.DRAFT,
                    created_at=now,
                    published_by=user_id,
                )

    def test_rules_count_property(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()
        rules = [
            Rule(
                id=f"rule-{i}",
                languages=["python"],
                message=f"Rule {i}",
                severity="ERROR",
                metadata={},
                patterns=[],
            )
            for i in range(6)
        ]

        rv = RuleVersion(
            id=uuid4(),
            version="0.1.0",
            rules=rules,
            status=RuleVersionStatus.ACTIVE,
            created_at=now,
            published_by=user_id,
        )

        assert rv.rules_count == 6

    def test_rule_version_frozen(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()

        rv = RuleVersion(
            id=uuid4(),
            version="0.1.0",
            rules=[],
            status=RuleVersionStatus.ACTIVE,
            created_at=now,
            published_by=user_id,
        )

        with pytest.raises(Exception):  # FrozenModelError
            rv.version = "0.2.0"  # type: ignore[misc]

    def test_rule_version_with_deprecated_at(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()

        rv = RuleVersion(
            id=uuid4(),
            version="0.1.0",
            rules=[],
            status=RuleVersionStatus.DEPRECATED,
            created_at=now,
            published_by=user_id,
            deprecated_at=now,
        )

        assert rv.status == RuleVersionStatus.DEPRECATED
        assert rv.deprecated_at is not None

    def test_rule_version_optional_fields(self) -> None:
        now = datetime.now(timezone.utc)
        user_id = uuid4()

        rv = RuleVersion(
            id=uuid4(),
            version="0.1.0",
            rules=[],
            status=RuleVersionStatus.DRAFT,
            created_at=now,
            published_by=user_id,
            notes=None,
            deprecated_at=None,
        )

        assert rv.notes is None
        assert rv.deprecated_at is None
