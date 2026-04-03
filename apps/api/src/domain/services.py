"""IncidentService — orchestrates domain logic, delegates to repository port."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.exceptions import (
    ActionItemNotFoundError,
    IncidentHasActiveRuleError,
    IncidentNotFoundError,
    ResponderNotFoundError,
)
from src.domain.models import (
    ActionItemPriority,
    ActionItemStatus,
    AttachmentExtractionStatus,
    AttachmentType,
    Category,
    DetectionMethod,
    Incident,
    IncidentActionItem,
    IncidentAttachment,
    IncidentResponder,
    IncidentTimelineEvent,
    PostmortemStatus,
    ResponderRole,
    RuleVersion,
    Severity,
    TimelineEventType,
)
from src.ports.action_item_repo import ActionItemRepoPort
from src.ports.attachment_repo import AttachmentRepoPort
from src.ports.incident_repo import IncidentRepoPort
from src.ports.responder_repo import ResponderRepoPort
from src.ports.rule_version_repo import RuleVersionRepository
from src.ports.timeline_event_repo import TimelineEventRepoPort


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


class TimelineEventService:
    def __init__(self, repo: TimelineEventRepoPort) -> None:
        self._repo = repo

    async def create(
        self,
        *,
        incident_id: UUID,
        event_type: TimelineEventType,
        description: str,
        occurred_at: datetime,
        recorded_by: UUID,
        duration_minutes: int | None = None,
        external_reference_url: str | None = None,
    ) -> IncidentTimelineEvent:
        now = datetime.now(UTC)
        event = IncidentTimelineEvent(
            id=uuid4(),
            incident_id=incident_id,
            event_type=event_type,
            description=description,
            occurred_at=occurred_at,
            recorded_by=recorded_by,
            duration_minutes=duration_minutes,
            external_reference_url=external_reference_url,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.create(event)

    async def list_by_incident(self, incident_id: UUID) -> list[IncidentTimelineEvent]:
        return await self._repo.list_by_incident(incident_id, order_asc=True)

    async def delete(self, event_id: UUID) -> None:
        await self._repo.delete(event_id)


class ResponderService:
    def __init__(self, repo: ResponderRepoPort) -> None:
        self._repo = repo

    async def add_responder(
        self,
        *,
        incident_id: UUID,
        user_id: UUID,
        role: ResponderRole,
        joined_at: datetime | None = None,
        contribution_summary: str | None = None,
    ) -> IncidentResponder:
        now = datetime.now(UTC)
        responder = IncidentResponder(
            id=uuid4(),
            incident_id=incident_id,
            user_id=user_id,
            role=role,
            joined_at=joined_at or now,
            contribution_summary=contribution_summary,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.create(responder)

    async def list_responders(self, incident_id: UUID) -> list[IncidentResponder]:
        return await self._repo.list_by_incident(incident_id)

    async def update_responder(
        self,
        responder_id: UUID,
        **fields: object,
    ) -> IncidentResponder:
        existing = await self._repo.get_by_id(responder_id)
        if existing is None:
            raise ResponderNotFoundError(str(responder_id))
        now = datetime.now(UTC)
        updated = existing.model_copy(update={**fields, "updated_at": now})
        return await self._repo.update(updated)

    async def remove_responder(self, responder_id: UUID) -> None:
        await self._repo.delete(responder_id)


class ActionItemService:
    def __init__(self, repo: ActionItemRepoPort) -> None:
        self._repo = repo

    async def create_action_item(
        self,
        *,
        incident_id: UUID,
        title: str,
        description: str | None = None,
        owner_id: UUID | None = None,
        priority: ActionItemPriority = ActionItemPriority.MEDIUM,
        due_date: date | None = None,
    ) -> IncidentActionItem:
        now = datetime.now(UTC)
        item = IncidentActionItem(
            id=uuid4(),
            incident_id=incident_id,
            title=title,
            description=description,
            owner_id=owner_id,
            status=ActionItemStatus.OPEN,
            priority=priority,
            due_date=due_date,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.create(item)

    async def list_action_items(
        self,
        incident_id: UUID,
        *,
        status: ActionItemStatus | None = None,
    ) -> list[IncidentActionItem]:
        return await self._repo.list_by_incident(incident_id, status_filter=status)

    async def update_action_item(
        self,
        item_id: UUID,
        **fields: object,
    ) -> IncidentActionItem:
        existing = await self._repo.get_by_id(item_id)
        if existing is None:
            raise ActionItemNotFoundError(str(item_id))
        now = datetime.now(UTC)
        update_data: dict[str, object] = {**fields, "updated_at": now}
        if (
            update_data.get("status") == ActionItemStatus.COMPLETED
            and existing.completed_at is None
            and "completed_at" not in update_data
        ):
            update_data["completed_at"] = now
        updated = existing.model_copy(update=update_data)
        return await self._repo.update(updated)

    async def delete_action_item(self, item_id: UUID) -> None:
        await self._repo.delete(item_id)


class AttachmentService:
    def __init__(self, repo: AttachmentRepoPort) -> None:
        self._repo = repo

    async def register_attachment(
        self,
        *,
        incident_id: UUID,
        uploaded_by: UUID | None = None,
        filename: str,
        mime_type: str,
        file_size_bytes: int,
        gcs_bucket: str,
        gcs_object_path: str,
        attachment_type: AttachmentType,
        source_system: str | None = None,
        source_url: str | None = None,
    ) -> IncidentAttachment:
        now = datetime.now(UTC)
        attachment = IncidentAttachment(
            id=uuid4(),
            incident_id=incident_id,
            uploaded_by=uploaded_by,
            filename=filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            gcs_bucket=gcs_bucket,
            gcs_object_path=gcs_object_path,
            extraction_status=AttachmentExtractionStatus.PENDING,
            attachment_type=attachment_type,
            source_system=source_system,
            source_url=source_url,
            created_at=now,
            updated_at=now,
        )
        return await self._repo.create(attachment)

    async def list_attachments(self, incident_id: UUID) -> list[IncidentAttachment]:
        return await self._repo.list_by_incident(incident_id)

    async def delete_attachment(self, attachment_id: UUID) -> None:
        await self._repo.delete(attachment_id)


# ─── Phase B: API Integration & Versioning ───────────────────────────────────


class RuleVersionService:
    """Service layer for rule versioning — orchestrates repository and cache."""

    def __init__(self, repo: RuleVersionRepository) -> None:
        self._repo = repo

    async def get_latest_active(self) -> RuleVersion | None:
        """Get the latest active rule version.

        Returns:
            RuleVersion with status='active' (most recently created), or None if none exists.
        """
        return await self._repo.get_latest_active()

    async def get_by_version(self, version: str) -> RuleVersion | None:
        """Get a specific rule version by version string.

        Args:
            version: Semantic version (e.g., "0.1.0")

        Returns:
            RuleVersion object (any status), or None if not found.
        """
        return await self._repo.get_by_version(version)

    async def list_all(self) -> list[RuleVersion]:
        """List all rule versions (all statuses) in creation order.

        Returns:
            List of RuleVersion objects ordered by created_at DESC.
        """
        return await self._repo.list_all()

    async def publish_version(
        self,
        version: str,
        rules_json: list[dict[str, Any]],
        published_by: UUID,
        notes: str | None = None,
    ) -> RuleVersion:
        """Publish a new rule version.

        Args:
            version: Semantic version (e.g., "0.2.0")
            rules_json: List of rule definitions
            published_by: UUID of publishing user
            notes: Optional release notes

        Returns:
            RuleVersion object with status='draft'

        Raises:
            VersionAlreadyExistsError: If version already exists
            InvalidVersionFormatError: If version doesn't match semver pattern
        """
        return await self._repo.publish_version(version, rules_json, str(published_by), notes)

    async def deprecate_version(self, version: str) -> RuleVersion:
        """Mark a rule version as deprecated.

        Args:
            version: Semantic version to deprecate

        Returns:
            Updated RuleVersion with status='deprecated'

        Raises:
            RuleVersionNotFoundError: If version not found
        """
        return await self._repo.deprecate_version(version)
