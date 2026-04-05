"""Domain services — IncidentService, AnalyticsService, and sub-resource services."""

from __future__ import annotations

import hashlib
import secrets
import time
from datetime import UTC, date, datetime, timedelta
from typing import Any, cast
from uuid import UUID, uuid4

from src.domain.exceptions import (
    ActionItemNotFoundError,
    ApiKeyInvalidError,
    ApiKeyRevokedError,
    IncidentHasActiveRuleError,
    IncidentMissingPostmortumError,
    IncidentNotFoundError,
    PostmortumAlreadyExistsError,
    PostmortumLockedError,
    ResponderNotFoundError,
)
from src.domain.models import (
    ActionItemPriority,
    ActionItemStatus,
    ApiKey,
    AttachmentExtractionStatus,
    AttachmentType,
    Category,
    DetectionMethod,
    Incident,
    IncidentActionItem,
    IncidentAttachment,
    IncidentResponder,
    IncidentTimelineEvent,
    Postmortem,
    PostmortemStatus,
    PostmortumSeverity,
    ResponderRole,
    RootCauseCategory,
    RuleVersion,
    Scan,
    Severity,
    TimelineEventType,
    User,
    _UnsetSentinel,
)
from src.ports.action_item_repo import ActionItemRepoPort
from src.ports.api_key_repo import ApiKeyRepoPort
from src.ports.attachment_repo import AttachmentRepoPort
from src.ports.incident_repo import IncidentRepoPort
from src.ports.postmortem_repo import PostmortumRepoPort
from src.ports.responder_repo import ResponderRepoPort
from src.ports.rule_version_repo import RuleVersionRepository
from src.ports.scan_repo import ScanRepoPort
from src.ports.timeline_event_repo import TimelineEventRepoPort
from src.ports.user_repo import UserRepoPort


class IncidentService:
    def __init__(
        self, repo: IncidentRepoPort, postmortem_repo: PostmortumRepoPort | None = None
    ) -> None:
        self._repo = repo
        self._postmortem_repo = postmortem_repo

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
        if existing.semgrep_rule_id and new_category != existing.category:
            raise IncidentHasActiveRuleError(str(incident_id), existing.semgrep_rule_id)

        update_data: dict[str, object] = {}
        allowed_fields = {
            "title",
            "date",
            "source_url",
            "organization",
            "category",
            "subcategory",
            "failure_mode",
            "severity",
            "affected_languages",
            "anti_pattern",
            "code_example",
            "remediation",
            "static_rule_possible",
            "semgrep_rule_id",
            "tags",
            "started_at",
            "detected_at",
            "ended_at",
            "resolved_at",
            "impact_summary",
            "customers_affected",
            "sla_breached",
            "slo_breached",
            "postmortem_status",
            "postmortem_published_at",
            "postmortem_due_date",
            "lessons_learned",
            "why_we_were_surprised",
            "detection_method",
            "slack_channel_id",
            "external_tracking_id",
            "incident_lead_id",
            "raw_content",
            "tech_context",
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

        # Enforce postmortem requirement: incident cannot be resolved without postmortem
        if (
            "resolved_at" in fields
            and fields.get("resolved_at") is not None
            and self._postmortem_repo is not None
        ):
            postmortem = await self._postmortem_repo.get_by_incident_id(incident_id)
            if postmortem is None:
                raise IncidentMissingPostmortumError(str(incident_id))

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
        status: str = "active",
    ) -> RuleVersion:
        """Publish a new rule version.

        Args:
            version: Semantic version (e.g., "0.2.0")
            rules_json: List of rule definitions
            published_by: UUID of publishing user
            notes: Optional release notes
            status: 'active' (default, immediately served) or 'draft' (editing only)

        Raises:
            VersionAlreadyExistsError: If version already exists
            InvalidVersionFormatError: If version doesn't match semver pattern
        """
        return await self._repo.publish_version(
            version, rules_json, str(published_by), notes, status=status
        )

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

    async def update_rules(
        self, version: str, rules_json: list[dict[str, Any]]
    ) -> RuleVersion:
        """Replace the rules list of an existing version in-place.

        Args:
            version: Semantic version string
            rules_json: New list of rule definitions

        Returns:
            Updated RuleVersion

        Raises:
            RuleVersionNotFoundError: If version not found
        """
        return await self._repo.update_rules(version, rules_json)


# ─── Phase C: Incident Knowledge Capture (Postmortem) ────────────────────────


class PostmortumService:
    """Service layer for postmortem root cause analysis."""

    def __init__(self, repo: PostmortumRepoPort) -> None:
        self._repo = repo

    async def create(
        self,
        *,
        incident_id: UUID,
        root_cause_category: RootCauseCategory,
        description: str,
        team_responsible: str,
        severity_for_rule: PostmortumSeverity,
        created_by: UUID,
        suggested_pattern: str | None = None,
        related_rule_id: str | None = None,
    ) -> Postmortem:
        """Create a postmortem for an incident.

        Args:
            incident_id: UUID of the incident being analyzed
            root_cause_category: Category of root cause (e.g., CODE_PATTERN, INFRASTRUCTURE)
            description: Detailed analysis (20-2000 characters)
            team_responsible: Team accountable for prevention (e.g., "backend", "security")
            severity_for_rule: Severity for prevention rule (ERROR or WARNING)
            created_by: UUID of the user creating the postmortem
            suggested_pattern: Optional regex or semgrep pattern to detect this issue
            related_rule_id: Optional reference to existing rule (e.g., "injection-001")

        Returns:
            Created Postmortem object

        Raises:
            PostmortumAlreadyExistsError: If postmortem already exists for incident
        """
        # Check if postmortem already exists
        existing = await self._repo.get_by_incident_id(incident_id)
        if existing is not None:
            raise PostmortumAlreadyExistsError(incident_id)

        now = datetime.now(UTC)
        postmortem = Postmortem(
            id=uuid4(),
            incident_id=incident_id,
            root_cause_category=root_cause_category,
            description=description,
            suggested_pattern=suggested_pattern,
            team_responsible=team_responsible,
            severity_for_rule=severity_for_rule,
            related_rule_id=related_rule_id,
            created_by=created_by,
            created_at=now,
            updated_by=None,
            updated_at=None,
            is_locked=False,
        )
        return await self._repo.create(postmortem)

    async def get_by_id(self, postmortem_id: UUID) -> Postmortem:
        """Retrieve postmortem by ID.

        Raises:
            PostmortumNotFoundError: If not found
        """
        return await self._repo.get_by_id(postmortem_id)

    async def get_by_incident_id(self, incident_id: UUID) -> Postmortem | None:
        """Retrieve postmortem by incident ID (1:1 relationship)."""
        return await self._repo.get_by_incident_id(incident_id)

    async def update(
        self,
        postmortem_id: UUID,
        **fields: object,
    ) -> Postmortem:
        """Update a postmortem (except is_locked, which is enforced at API level).

        Raises:
            PostmortumNotFoundError: If not found
            PostmortumLockedError: If postmortem is locked
        """
        existing = await self._repo.get_by_id(postmortem_id)
        if existing.is_locked:
            raise PostmortumLockedError(postmortem_id)

        update_data: dict[str, object] = {}
        allowed_fields = {
            "root_cause_category",
            "description",
            "suggested_pattern",
            "team_responsible",
            "severity_for_rule",
            "related_rule_id",
        }
        for key, value in fields.items():
            if key in allowed_fields:
                update_data[key] = value

        if not update_data:
            return existing

        # Convert string enums back to domain enums if needed
        if "root_cause_category" in update_data:
            val = update_data["root_cause_category"]
            if isinstance(val, str):
                update_data["root_cause_category"] = RootCauseCategory(val)

        if "severity_for_rule" in update_data:
            val = update_data["severity_for_rule"]
            if isinstance(val, str):
                update_data["severity_for_rule"] = PostmortumSeverity(val)

        now = datetime.now(UTC)
        updated = existing.model_copy(
            update={
                **update_data,
                "updated_by": existing.created_by,  # Placeholder; API will set actual user
                "updated_at": now,
            }
        )
        return await self._repo.update(updated)

    async def lock(self, postmortem_id: UUID) -> Postmortem:
        """Lock a postmortem after incident resolution (immutable audit trail).

        Raises:
            PostmortumNotFoundError: If not found
        """
        existing = await self._repo.get_by_id(postmortem_id)
        now = datetime.now(UTC)
        locked = existing.model_copy(
            update={
                "is_locked": True,
                "updated_at": now,
            }
        )
        return await self._repo.update(locked)

    async def list_all(self) -> list[Postmortem]:
        """List all postmortems for analytics and reporting."""
        return await self._repo.list_all()


# ─── Phase C.2: Analytics Service ────────────────────────────────────────────

import calendar  # noqa: E402

import structlog as _structlog  # noqa: E402

from src.adapters.postgres.analytics_cache import AnalyticsCache  # noqa: E402
from src.domain.models import (  # noqa: E402
    AnalyticsFilter,
    AnalyticsPeriod,
    AnalyticsSummary,
    CategoryStats,
    RuleEffectivenessStats,
    SeverityTrendPoint,
    TeamStats,
    TimelinePoint,
)
from src.ports.analytics import AnalyticsRepoPort  # noqa: E402

_analytics_logger = _structlog.get_logger(__name__)


class AnalyticsService:
    """Orchestrates analytics queries with period parsing, normalization, and caching."""

    def __init__(self, repo: AnalyticsRepoPort, cache: AnalyticsCache | None = None) -> None:
        self._repo = repo
        self._cache = cache

    def _cache_get(self, method: str, params: dict[str, Any]) -> Any | None:
        if self._cache is None:
            return None
        return self._cache.get(AnalyticsCache.make_key(method, params))

    def _cache_set(self, method: str, params: dict[str, Any], value: Any) -> None:
        if self._cache is not None:
            self._cache.set(AnalyticsCache.make_key(method, params), value)

    def _cache_key(
        self, method: str, filters: AnalyticsFilter, start: Any, end: Any, **extra: Any
    ) -> dict[str, Any]:
        return {
            "method": method,
            **filters.model_dump(),
            "start": str(start),
            "end": str(end),
            **extra,
        }

    async def get_summary(
        self, period: AnalyticsPeriod, filters: AnalyticsFilter
    ) -> AnalyticsSummary:
        """Return total/resolved/unresolved counts and avg resolution days."""
        t0 = time.monotonic()
        start, end = self._parse_period(period)
        ck = self._cache_key("summary", filters, start, end)
        if (cached := self._cache_get("summary", ck)) is not None:
            return cast(AnalyticsSummary, cached)
        result = await self._repo.get_summary(start, end, filters)
        self._cache_set("summary", ck, result)
        elapsed_ms = (time.monotonic() - t0) * 1000
        _analytics_logger.info(
            "analytics.service",
            method="get_summary",
            elapsed_ms=round(elapsed_ms, 1),
            analytics_dashboard_load_time_ms=round(elapsed_ms, 1),
            analytics_query_result_count=1,
        )
        return result

    async def get_by_category(
        self, period: AnalyticsPeriod, filters: AnalyticsFilter
    ) -> list[CategoryStats]:
        """Return incident stats grouped by category, sorted by count DESC."""
        t0 = time.monotonic()
        start, end = self._parse_period(period)
        ck = self._cache_key("by_category", filters, start, end)
        if (cached := self._cache_get("by_category", ck)) is not None:
            return cast(list[CategoryStats], cached)
        stats = await self._repo.get_by_category(start, end, filters)
        stats = self._normalize_stats(stats)
        self._cache_set("by_category", ck, stats)
        elapsed_ms = (time.monotonic() - t0) * 1000
        _analytics_logger.info(
            "analytics.service",
            method="get_by_category",
            elapsed_ms=round(elapsed_ms, 1),
            analytics_query_result_count=len(stats),
        )
        return stats

    async def get_by_team(
        self, period: AnalyticsPeriod, filters: AnalyticsFilter
    ) -> list[TeamStats]:
        """Return incident stats grouped by team, sorted by count DESC."""
        t0 = time.monotonic()
        start, end = self._parse_period(period)
        ck = self._cache_key("by_team", filters, start, end)
        if (cached := self._cache_get("by_team", ck)) is not None:
            return cast(list[TeamStats], cached)
        result = await self._repo.get_by_team(start, end, filters)
        self._cache_set("by_team", ck, result)
        elapsed_ms = (time.monotonic() - t0) * 1000
        _analytics_logger.info(
            "analytics.service",
            method="get_by_team",
            elapsed_ms=round(elapsed_ms, 1),
            analytics_query_result_count=len(result),
        )
        return result

    async def get_timeline(
        self, period: AnalyticsPeriod, filters: AnalyticsFilter
    ) -> list[TimelinePoint]:
        """Return weekly timeline points for the period (minimum 52 weeks)."""
        t0 = time.monotonic()
        start, end = self._parse_period(period)
        ck = self._cache_key("timeline", filters, start, end)
        if (cached := self._cache_get("timeline", ck)) is not None:
            return cast(list[TimelinePoint], cached)
        result = await self._repo.get_timeline(start, end, filters)
        self._cache_set("timeline", ck, result)
        elapsed_ms = (time.monotonic() - t0) * 1000
        _analytics_logger.info(
            "analytics.service",
            method="get_timeline",
            elapsed_ms=round(elapsed_ms, 1),
            analytics_query_result_count=len(result),
        )
        return result

    async def get_severity_trend(
        self, period: AnalyticsPeriod, filters: AnalyticsFilter
    ) -> list[SeverityTrendPoint]:
        """Return weekly ERROR vs WARNING counts."""
        t0 = time.monotonic()
        start, end = self._parse_period(period)
        ck = self._cache_key("severity_trend", filters, start, end)
        if (cached := self._cache_get("severity_trend", ck)) is not None:
            return cast(list[SeverityTrendPoint], cached)
        result = await self._repo.get_severity_trend(start, end, filters)
        self._cache_set("severity_trend", ck, result)
        elapsed_ms = (time.monotonic() - t0) * 1000
        _analytics_logger.info(
            "analytics.service",
            method="get_severity_trend",
            elapsed_ms=round(elapsed_ms, 1),
            analytics_query_result_count=len(result),
        )
        return result

    async def get_top_rules(
        self, period: AnalyticsPeriod, filters: AnalyticsFilter, top_n: int = 5
    ) -> list[RuleEffectivenessStats]:
        """Return top N rules by incident count."""
        t0 = time.monotonic()
        start, end = self._parse_period(period)
        ck = self._cache_key("top_rules", filters, start, end, top_n=top_n)
        if (cached := self._cache_get("top_rules", ck)) is not None:
            return cast(list[RuleEffectivenessStats], cached)
        result = await self._repo.get_top_rules(start, end, filters, top_n)
        self._cache_set("top_rules", ck, result)
        elapsed_ms = (time.monotonic() - t0) * 1000
        _analytics_logger.info(
            "analytics.service",
            method="get_top_rules",
            elapsed_ms=round(elapsed_ms, 1),
            analytics_query_result_count=len(result),
        )
        return result

    def _parse_period(self, period: AnalyticsPeriod) -> tuple[datetime, datetime]:
        """Convert AnalyticsPeriod to (start, end) datetime range (UTC-naive).

        - "week"    → last 7 days
        - "month"   → last 30 days
        - "quarter" → start of current calendar quarter to today (quarter-to-date)
                      Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec
                      end = min(today, end_of_quarter)
        - "custom"  → period.start_date to period.end_date (caller validated)
        """
        now = datetime.now(UTC)
        today = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if period.value == "week":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
            return start, today

        if period.value == "month":
            start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            return start, today

        if period.value == "quarter":
            month = now.month
            # Q1=1-3, Q2=4-6, Q3=7-9, Q4=10-12
            quarter_start_month = ((month - 1) // 3) * 3 + 1
            quarter_end_month = quarter_start_month + 2
            last_day = calendar.monthrange(now.year, quarter_end_month)[1]
            quarter_end = datetime(
                now.year, quarter_end_month, last_day, 23, 59, 59, 999999, tzinfo=UTC
            )
            start = datetime(now.year, quarter_start_month, 1, 0, 0, 0, 0, tzinfo=UTC)
            end = min(today, quarter_end)
            return start, end

        # "custom"
        # start_date/end_date validated at API layer (T049)
        assert period.start_date is not None
        assert period.end_date is not None
        return period.start_date, period.end_date

    def _normalize_stats(self, stats: list[CategoryStats]) -> list[CategoryStats]:
        """Ensure percentages sum to 100 (correct floating-point rounding drift)."""
        if not stats:
            return stats
        total_pct = sum(s.percentage for s in stats)
        if total_pct == 0:
            return stats
        # Re-normalize so sum equals exactly 100
        factor = 100.0 / total_pct
        normalized = []
        for s in stats:
            normalized.append(
                s.model_copy(update={"percentage": round(s.percentage * factor, 2)})
            )
        return normalized


# ─── Phase 2: Navigation, Dashboard & User Profile ───────────────────────────


class UserService:
    """Thin orchestrator for user profile operations."""

    def __init__(self, repo: UserRepoPort) -> None:
        self._repo = repo

    async def get_or_create(
        self, firebase_uid: str, email: str, display_name: str | None
    ) -> User:
        """Get or create a user record — display_name only written on first creation."""
        return await self._repo.get_or_create(firebase_uid, email, display_name)

    async def update_profile(
        self,
        user_id: UUID,
        display_name: str | None,
        job_title: str | None | _UnsetSentinel,
    ) -> User:
        """Update user profile fields.

        display_name: None = don't update; str = update to value.
        job_title: UNSET = don't update; None = clear to null; str = update to value.
        Raises ValueError if display_name is an empty string.
        Raises UserNotFoundError if no user with user_id exists.
        """
        if display_name is not None and len(display_name.strip()) == 0:
            raise ValueError("display_name cannot be empty string")
        return await self._repo.update(user_id, display_name, job_title)


# ─── Phase 4: Semgrep Platform — API Keys & Scans ────────────────────────────


class ApiKeyService:
    """Service layer for API key management."""

    def __init__(self, repo: ApiKeyRepoPort) -> None:
        self._repo = repo

    def _generate_token(self) -> str:
        """Generate a unique API key token: tlp_ + 32 random hex chars."""
        return f"tlp_{secrets.token_hex(32)}"

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def create(self, owner_id: UUID, name: str) -> tuple[str, ApiKey]:
        """Create API key. Returns (raw_token, ApiKey). raw_token shown ONCE."""
        token = self._generate_token()
        key_hash = self._hash_token(token)
        prefix = token[:7]  # "tlp_abc"
        api_key = await self._repo.create(owner_id, name, key_hash, prefix)
        return token, api_key

    async def list_by_user(self, owner_id: UUID) -> list[ApiKey]:
        return await self._repo.list_by_owner(owner_id)

    async def revoke(self, key_id: UUID, owner_id: UUID) -> ApiKey:
        return await self._repo.revoke(key_id, owner_id)

    async def validate(self, raw_token: str) -> ApiKey:
        """Validate raw token. Raises ApiKeyInvalidError or ApiKeyRevokedError."""
        key_hash = self._hash_token(raw_token)
        key = await self._repo.get_by_hash(key_hash)
        if key is None:
            raise ApiKeyInvalidError()
        if key.is_revoked:
            raise ApiKeyRevokedError(str(key.id))
        await self._repo.mark_used(key.id)
        return key

    async def get_whitelist(self, key_id: UUID) -> list[str]:
        return await self._repo.get_whitelist(key_id)

    async def add_to_whitelist(self, key_id: UUID, rule_id: str) -> None:
        await self._repo.add_to_whitelist(key_id, rule_id)

    async def remove_from_whitelist(self, key_id: UUID, rule_id: str) -> None:
        await self._repo.remove_from_whitelist(key_id, rule_id)


class ScanService:
    """Service layer for scan registration and reporting."""

    def __init__(self, repo: ScanRepoPort, api_key_repo: ApiKeyRepoPort) -> None:
        self._repo = repo
        self._api_key_repo = api_key_repo

    async def register(
        self,
        api_key: ApiKey,
        repository: str,
        branch: str,
        pr_number: int | None,
        rules_version: str,
        findings_count: int,
        errors_count: int,
        warnings_count: int,
        duration_ms: int,
        findings: list[dict[str, str | int]],
    ) -> Scan:
        return await self._repo.create_with_findings(
            api_key_id=api_key.id,
            repository=repository,
            branch=branch,
            pr_number=pr_number,
            rules_version=rules_version,
            findings_count=findings_count,
            errors_count=errors_count,
            warnings_count=warnings_count,
            duration_ms=duration_ms,
            findings=findings,
        )

    async def list_by_user(self, owner_id: UUID) -> list[Scan]:
        return await self._repo.list_by_owner(owner_id)

    async def get_summary(self, owner_id: UUID) -> dict[str, object]:
        return await self._repo.get_summary(owner_id)

    async def get_global_metrics(self) -> dict[str, object]:
        return await self._repo.get_global_metrics()
