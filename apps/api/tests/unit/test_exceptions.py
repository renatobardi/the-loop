"""Unit tests for domain exceptions."""

from src.domain.exceptions import (
    DuplicateSourceUrlError,
    IncidentHasActiveRuleError,
    IncidentNotFoundError,
    OptimisticLockError,
)


class TestIncidentNotFoundError:
    def test_message(self) -> None:
        err = IncidentNotFoundError("abc-123")
        assert "abc-123" in str(err)
        assert err.incident_id == "abc-123"


class TestDuplicateSourceUrlError:
    def test_message(self) -> None:
        err = DuplicateSourceUrlError("https://example.com")
        assert "https://example.com" in str(err)
        assert err.source_url == "https://example.com"


class TestOptimisticLockError:
    def test_message(self) -> None:
        err = OptimisticLockError("abc-123", 5)
        assert "abc-123" in str(err)
        assert "5" in str(err)
        assert err.current_version == 5


class TestIncidentHasActiveRuleError:
    def test_message(self) -> None:
        err = IncidentHasActiveRuleError("abc-123", "injection-001")
        assert "abc-123" in str(err)
        assert "injection-001" in str(err)
        assert err.semgrep_rule_id == "injection-001"
