"""IncidentService — orchestrates domain logic, delegates to repository port."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.exceptions import (
    IncidentHasActiveRuleError,
    IncidentNotFoundError,
)
from src.domain.models import Category, Incident, Severity
from src.ports.incident_repo import IncidentRepoPort


class IncidentService:
    def __init__(self, repo: IncidentRepoPort) -> None:
        self._repo = repo

    async def create(
        self,
        *,
        title: str,
        category: Category,
        severity: Severity,
        anti_pattern: str,
        remediation: str,
        created_by: UUID,
        date: str | None = None,
        source_url: str | None = None,
        organization: str | None = None,
        subcategory: str | None = None,
        failure_mode: str | None = None,
        affected_languages: list[str] | None = None,
        code_example: str | None = None,
        static_rule_possible: bool = False,
        semgrep_rule_id: str | None = None,
        tags: list[str] | None = None,
    ) -> Incident:
        now = datetime.now(UTC)
        incident = Incident(
            id=uuid4(),
            title=title,
            date=date,  # type: ignore[arg-type]
            source_url=source_url or None,
            organization=organization,
            category=category,
            subcategory=subcategory,
            failure_mode=failure_mode,
            severity=severity,
            affected_languages=affected_languages or [],
            anti_pattern=anti_pattern,
            code_example=code_example,
            remediation=remediation,
            static_rule_possible=static_rule_possible,
            semgrep_rule_id=semgrep_rule_id,
            embedding=None,
            tags=tags or [],
            version=1,
            deleted_at=None,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )
        return await self._repo.create(incident)

    async def get_by_id(self, incident_id: UUID) -> Incident:
        incident = await self._repo.get_by_id(incident_id)
        if incident is None:
            raise IncidentNotFoundError(str(incident_id))
        return incident

    async def update(
        self,
        incident_id: UUID,
        expected_version: int,
        **fields: object,
    ) -> Incident:
        existing = await self._repo.get_by_id(incident_id)
        if existing is None:
            raise IncidentNotFoundError(str(incident_id))

        new_category = fields.get("category", existing.category)
        if (
            existing.semgrep_rule_id
            and new_category != existing.category
        ):
            raise IncidentHasActiveRuleError(str(incident_id), existing.semgrep_rule_id)

        update_data: dict[str, object] = {}
        allowed_fields = {
            "title", "date", "source_url", "organization", "category",
            "subcategory", "failure_mode", "severity", "affected_languages",
            "anti_pattern", "code_example", "remediation", "static_rule_possible",
            "semgrep_rule_id", "tags",
        }
        for key, value in fields.items():
            if key in allowed_fields:
                update_data[key] = value

        updated = existing.model_copy(update=update_data)
        return await self._repo.update(updated, expected_version)

    async def soft_delete(self, incident_id: UUID) -> None:
        existing = await self._repo.get_by_id(incident_id)
        if existing is None:
            raise IncidentNotFoundError(str(incident_id))

        if existing.semgrep_rule_id:
            raise IncidentHasActiveRuleError(str(incident_id), existing.semgrep_rule_id)

        await self._repo.soft_delete(incident_id)

    async def list_incidents(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        category: Category | None = None,
        severity: Severity | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Incident], int]:
        per_page = max(1, min(per_page, 100))
        page = max(1, page)
        return await self._repo.list_incidents(
            page=page,
            per_page=per_page,
            category=category,
            severity=severity,
            keyword=keyword,
        )
