"""Unit tests for rule API models — validation and schema."""

from pydantic import ValidationError

import pytest

from src.api.models.rules import DeprecateRulesRequest


class TestDeprecateRulesRequest:
    """Tests for DeprecateRulesRequest validation."""

    def test_valid_semver(self) -> None:
        """Test DeprecateRulesRequest accepts valid semver."""
        req = DeprecateRulesRequest(version="0.1.0")
        assert req.version == "0.1.0"

    def test_valid_semver_large(self) -> None:
        """Test DeprecateRulesRequest accepts large version numbers."""
        req = DeprecateRulesRequest(version="10.20.30")
        assert req.version == "10.20.30"

    def test_invalid_semver_no_patch(self) -> None:
        """Test DeprecateRulesRequest rejects version without patch."""
        with pytest.raises(ValidationError) as exc_info:
            DeprecateRulesRequest(version="0.1")
        assert "Invalid semantic version format" in str(exc_info.value)

    def test_invalid_semver_extra_number(self) -> None:
        """Test DeprecateRulesRequest rejects version with extra component."""
        with pytest.raises(ValidationError) as exc_info:
            DeprecateRulesRequest(version="0.1.0.0")
        assert "Invalid semantic version format" in str(exc_info.value)

    def test_invalid_semver_letters(self) -> None:
        """Test DeprecateRulesRequest rejects version with letters."""
        with pytest.raises(ValidationError) as exc_info:
            DeprecateRulesRequest(version="0.1.a")
        assert "Invalid semantic version format" in str(exc_info.value)

    def test_invalid_semver_empty(self) -> None:
        """Test DeprecateRulesRequest rejects empty version."""
        with pytest.raises(ValidationError) as exc_info:
            DeprecateRulesRequest(version="")
        assert "Invalid semantic version format" in str(exc_info.value)
