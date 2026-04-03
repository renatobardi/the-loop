"""Port (protocol) for RuleVersionRepository — Phase B API integration."""

from typing import Any

from src.domain.models import RuleVersion

__all__ = ["RuleVersionRepository"]


class RuleVersionRepository:
    """Interface for accessing and managing rule versions."""

    async def get_latest_active(self) -> RuleVersion | None:
        """Get the latest active rule version.

        Returns:
            RuleVersion with status='active' (most recently created), or None if
            no active version exists.
        """
        raise NotImplementedError()

    async def get_by_version(self, version: str) -> RuleVersion | None:
        """Get a specific rule version by version string.

        Args:
            version: Semantic version (e.g., "0.1.0")

        Returns:
            RuleVersion object, or None if version not found (regardless of status).
        """
        raise NotImplementedError()

    async def list_all(self) -> list[RuleVersion]:
        """List all rule versions (all statuses) in creation order.

        Returns:
            List of RuleVersion objects ordered by created_at DESC.
        """
        raise NotImplementedError()

    async def publish_version(
        self,
        version: str,
        rules_json: list[dict[str, Any]],
        published_by: str,
        notes: str | None = None,
    ) -> RuleVersion:
        """Publish a new rule version.

        Args:
            version: Semantic version string (must pass validation)
            rules_json: List of rule definitions
            published_by: UUID of publishing user
            notes: Optional release notes

        Returns:
            RuleVersion object created with status='draft'

        Raises:
            VersionAlreadyExistsError: If version already exists (UNIQUE constraint)
            InvalidVersionFormatError: If version doesn't match semver pattern
        """
        raise NotImplementedError()

    async def deprecate_version(self, version: str) -> RuleVersion:
        """Mark a rule version as deprecated.

        Args:
            version: Semantic version string to deprecate

        Returns:
            Updated RuleVersion object with status='deprecated' and deprecated_at set

        Raises:
            RuleVersionNotFoundError: If version not found
        """
        raise NotImplementedError()
