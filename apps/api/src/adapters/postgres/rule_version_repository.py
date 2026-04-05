"""PostgreSQL adapter for RuleVersionRepository — Phase B API integration."""

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import (
    InvalidVersionFormatError,
    RuleVersionNotFoundError,
    VersionAlreadyExistsError,
)
from src.domain.models import Rule, RuleVersion, RuleVersionStatus
from src.ports.rule_version_repo import RuleVersionRepository

from .models import RuleVersionRow


class PostgresRuleVersionRepository(RuleVersionRepository):
    """PostgreSQL implementation of RuleVersionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _row_to_domain(self, row: RuleVersionRow) -> RuleVersion:
        """Convert ORM row to domain model.

        Raises:
            RuleVersionNotFoundError: If rules_json is malformed or missing required fields.
        """
        try:
            # Parse rules_json JSONB into Rule objects
            if isinstance(row.rules_json, str):
                rules_data = json.loads(row.rules_json)
            else:
                rules_data = row.rules_json

            if not isinstance(rules_data, list):
                raise ValueError("rules_json must be an array")

            rules = [Rule(**rule_data) for rule_data in rules_data]
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as e:
            raise RuleVersionNotFoundError(row.version) from e

        return RuleVersion(
            id=row.id,
            version=row.version,
            rules=rules,
            status=RuleVersionStatus(row.status),
            created_at=row.created_at,
            published_by=row.published_by,
            notes=row.notes,
            deprecated_at=row.deprecated_at,
        )

    async def get_latest_active(self) -> RuleVersion | None:
        """Get the latest active rule version (most recently created)."""
        stmt = (
            select(RuleVersionRow)
            .where(RuleVersionRow.status == "active")
            .order_by(desc(RuleVersionRow.created_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        row = result.scalars().first()
        return self._row_to_domain(row) if row else None

    async def get_by_version(self, version: str) -> RuleVersion | None:
        """Get a specific rule version by version string."""
        stmt = select(RuleVersionRow).where(RuleVersionRow.version == version)
        result = await self.session.execute(stmt)
        row = result.scalars().first()
        return self._row_to_domain(row) if row else None

    async def list_all(self) -> list[RuleVersion]:
        """List all rule versions (all statuses) in reverse creation order."""
        stmt = select(RuleVersionRow).order_by(desc(RuleVersionRow.created_at))
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [self._row_to_domain(row) for row in rows]

    async def update_rules(
        self, version: str, rules_json: list[dict[str, Any]]
    ) -> RuleVersion:
        """Replace the rules list of an existing version in-place."""
        stmt = select(RuleVersionRow).where(RuleVersionRow.version == version)
        result = await self.session.execute(stmt)
        row = result.scalars().first()
        if not row:
            raise RuleVersionNotFoundError(version)
        row.rules_json = rules_json  # type: ignore[assignment]  # JSONB accepts list
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(row)
        return self._row_to_domain(row)

    async def publish_version(
        self,
        version: str,
        rules_json: list[dict[str, Any]],
        published_by: str,
        notes: str | None = None,
        status: str = "active",
    ) -> RuleVersion:
        """Publish a new rule version.

        Args:
            status: Initial status — 'active' for immediate serving, 'draft' for editing.

        Raises:
            VersionAlreadyExistsError: If version already exists
            InvalidVersionFormatError: If version doesn't match semver pattern
        """
        # Validate semver format (domain model does this, but catch early)
        if not version or not _is_semver(version):
            raise InvalidVersionFormatError(version)

        # Check if version already exists before attempting insert
        stmt = select(RuleVersionRow).where(RuleVersionRow.version == version)
        result = await self.session.execute(stmt)
        if result.scalars().first():
            raise VersionAlreadyExistsError(version)

        # Serialize rules_json list to JSONB
        rules_json_str = json.dumps(rules_json)

        # Convert published_by string to UUID
        published_by_uuid = UUID(published_by) if isinstance(published_by, str) else published_by

        row = RuleVersionRow(
            version=version,
            rules_json=rules_json_str,
            status=status,
            published_by=published_by_uuid,
            notes=notes,
        )
        self.session.add(row)

        try:
            await self.session.flush()  # Flush to detect constraint violations
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            error_str = str(e).lower()
            # Fallback: check error message for constraint violation
            if "unique constraint" in error_str or "version" in error_str:
                raise VersionAlreadyExistsError(version) from e
            raise

        await self.session.refresh(row)
        return self._row_to_domain(row)

    async def deprecate_version(self, version: str) -> RuleVersion:
        """Mark a rule version as deprecated.

        Raises:
            RuleVersionNotFoundError: If version not found
        """
        stmt = select(RuleVersionRow).where(RuleVersionRow.version == version)
        result = await self.session.execute(stmt)
        row = result.scalars().first()

        if not row:
            raise RuleVersionNotFoundError(version)

        row.status = "deprecated"
        row.deprecated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(row)

        return self._row_to_domain(row)


def _is_semver(version: str) -> bool:
    """Check if version matches semantic versioning pattern (X.Y.Z)."""
    import re

    return bool(re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version))
