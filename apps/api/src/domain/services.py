"""IncidentService — orchestrates domain logic, delegates to repository port."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from src.domain.exceptions import (
    IncidentHasActiveRuleError,
    IncidentNotFoundError,
)
from src.domain.models import (
    Category,
    DetectionMethod,
    Incident,
    PostmortemStatus,
    Severity,
)
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
        started_at: datetime | None = None,
        detected_at: datetime | None = None,
        ended_at: datetime | None = None,
        resolved_at: datetime | None = None,
        impact_summary: str | None = None,
        customers_affected: int | None = None,
        sla_breached: bool = False,
        slo_breached: bool = False,
        postmortem_status: PostmortemStatus = PostmortemStatus.DRAFT,
        postmortem_published_at: datetime | None = None,
        postmortem_due_date: date | None = None,
        lessons_learned: str | None = None,
        why_we_were_surprised: str | None = None,
        detection_method: DetectionMethod | None = None,
        slack_channel_id: str | None = None,
        external_tracking_id: str | None = None,
        incident_lead_id: UUID | None = None,
        raw_content: dict[str, object] | None = None,
        tech_context: dict[str, object] | None = None,
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
            started_at=started_at,
            detected_at=detected_at,
            ended_at=ended_at,
            resolved_at=resolved_at,
            impact_summary=impact_summary,
            customers_affected=customers_affected,
            sla_breached=sla_breached,
            slo_breached=slo_breached,
            postmortem_status=postmortem_status,
            postmortem_published_at=postmortem_published_at,
            postmortem_due_date=postmortem_due_date,
            lessons_learned=lessons_learned,
            why_we_were_surprised=why_we_were_surprised,
            detection_method=detection_method,
            slack_channel_id=slack_channel_id,
            external_tracking_id=external_tracking_id,
            incident_lead_id=incident_lead_id,
            raw_content=raw_content,
            tech_context=tech_context,
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
            "started_at", "detected_at", "ended_at", "resolved_at",
            "impact_summary", "customers_affected", "sla_breached", "slo_breached",
            "postmortem_status", "postmortem_published_at", "postmortem_due_date",
            "lessons_learned", "why_we_were_surprised", "detection_method",
            "slack_channel_id", "external_tracking_id", "incident_lead_id",
            "raw_content", "tech_context",
        }
        for key, value in fields.items():
            if key in allowed_fields:
                update_data[key] = value

        # Auto-populate postmortem_published_at on first transition to PUBLISHED
        if (
            update_data.get("postmortem_status") == PostmortemStatus.PUBLISHED
            and existing.postmortem_published_at is None
            and "postmortem_published_at" not in update_data
        ):
            update_data["postmortem_published_at"] = datetime.now(UTC)

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
