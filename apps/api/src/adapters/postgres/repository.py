"""PostgreSQL adapter implementing IncidentRepoPort."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import IncidentRow
from src.domain.exceptions import DuplicateSourceUrlError, OptimisticLockError
from src.domain.models import Category, DetectionMethod, Incident, PostmortemStatus, Severity


def _row_to_domain(row: IncidentRow) -> Incident:
    return Incident(
        id=row.id,
        title=row.title,
        date=row.date,
        source_url=row.source_url,
        organization=row.organization,
        category=Category(row.category),
        subcategory=row.subcategory,
        failure_mode=row.failure_mode,
        severity=Severity(row.severity),
        affected_languages=row.affected_languages,
        anti_pattern=row.anti_pattern,
        code_example=row.code_example,
        remediation=row.remediation,
        static_rule_possible=row.static_rule_possible,
        semgrep_rule_id=row.semgrep_rule_id,
        embedding=None,
        tags=row.tags,
        version=row.version,
        deleted_at=row.deleted_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
        created_by=row.created_by,
        started_at=row.started_at,
        detected_at=row.detected_at,
        ended_at=row.ended_at,
        resolved_at=row.resolved_at,
        impact_summary=row.impact_summary,
        customers_affected=row.customers_affected,
        sla_breached=row.sla_breached,
        slo_breached=row.slo_breached,
        postmortem_status=PostmortemStatus(row.postmortem_status),
        postmortem_published_at=row.postmortem_published_at,
        postmortem_due_date=row.postmortem_due_date,
        lessons_learned=row.lessons_learned,
        why_we_were_surprised=row.why_we_were_surprised,
        detection_method=DetectionMethod(row.detection_method) if row.detection_method else None,
        slack_channel_id=row.slack_channel_id,
        external_tracking_id=row.external_tracking_id,
        incident_lead_id=row.incident_lead_id,
        raw_content=row.raw_content,
        tech_context=row.tech_context,
    )


class PostgresIncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, incident: Incident) -> Incident:
        row = IncidentRow(
            id=incident.id,
            title=incident.title,
            date=incident.date,
            source_url=incident.source_url,
            organization=incident.organization,
            category=incident.category.value,
            subcategory=incident.subcategory,
            failure_mode=incident.failure_mode,
            severity=incident.severity.value,
            affected_languages=incident.affected_languages,
            anti_pattern=incident.anti_pattern,
            code_example=incident.code_example,
            remediation=incident.remediation,
            static_rule_possible=incident.static_rule_possible,
            semgrep_rule_id=incident.semgrep_rule_id,
            tags=incident.tags,
            version=1,
            created_at=incident.created_at,
            updated_at=incident.updated_at,
            created_by=incident.created_by,
            started_at=incident.started_at,
            detected_at=incident.detected_at,
            ended_at=incident.ended_at,
            resolved_at=incident.resolved_at,
            impact_summary=incident.impact_summary,
            customers_affected=incident.customers_affected,
            sla_breached=incident.sla_breached,
            slo_breached=incident.slo_breached,
            postmortem_status=incident.postmortem_status.value,
            postmortem_published_at=incident.postmortem_published_at,
            postmortem_due_date=incident.postmortem_due_date,
            lessons_learned=incident.lessons_learned,
            why_we_were_surprised=incident.why_we_were_surprised,
            detection_method=(
                incident.detection_method.value if incident.detection_method else None
            ),
            slack_channel_id=incident.slack_channel_id,
            external_tracking_id=incident.external_tracking_id,
            incident_lead_id=incident.incident_lead_id,
            raw_content=incident.raw_content,
            tech_context=incident.tech_context,
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            if "uq_incidents_source_url" in str(e):
                raise DuplicateSourceUrlError(incident.source_url or "") from e
            raise
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_domain(row)

    async def get_by_id(self, incident_id: UUID) -> Incident | None:
        stmt = select(IncidentRow).where(
            IncidentRow.id == incident_id,
            IncidentRow.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _row_to_domain(row) if row else None

    async def update(self, incident: Incident, expected_version: int) -> Incident:
        now = datetime.now(timezone.utc)
        stmt = (
            update(IncidentRow)
            .where(
                IncidentRow.id == incident.id,
                IncidentRow.version == expected_version,
                IncidentRow.deleted_at.is_(None),
            )
            .values(
                title=incident.title,
                date=incident.date,
                source_url=incident.source_url,
                organization=incident.organization,
                category=incident.category.value,
                subcategory=incident.subcategory,
                failure_mode=incident.failure_mode,
                severity=incident.severity.value,
                affected_languages=incident.affected_languages,
                anti_pattern=incident.anti_pattern,
                code_example=incident.code_example,
                remediation=incident.remediation,
                static_rule_possible=incident.static_rule_possible,
                semgrep_rule_id=incident.semgrep_rule_id,
                tags=incident.tags,
                version=expected_version + 1,
                updated_at=now,
                started_at=incident.started_at,
                detected_at=incident.detected_at,
                ended_at=incident.ended_at,
                resolved_at=incident.resolved_at,
                impact_summary=incident.impact_summary,
                customers_affected=incident.customers_affected,
                sla_breached=incident.sla_breached,
                slo_breached=incident.slo_breached,
                postmortem_status=incident.postmortem_status.value,
                postmortem_published_at=incident.postmortem_published_at,
                postmortem_due_date=incident.postmortem_due_date,
                lessons_learned=incident.lessons_learned,
                why_we_were_surprised=incident.why_we_were_surprised,
                detection_method=(
                    incident.detection_method.value if incident.detection_method else None
                ),
                slack_channel_id=incident.slack_channel_id,
                external_tracking_id=incident.external_tracking_id,
                incident_lead_id=incident.incident_lead_id,
                raw_content=incident.raw_content,
                tech_context=incident.tech_context,
            )
            .returning(IncidentRow)
        )
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            await self._session.rollback()
            if "uq_incidents_source_url" in str(e):
                raise DuplicateSourceUrlError(incident.source_url or "") from e
            raise
        row = result.scalar_one_or_none()
        if row is None:
            existing = await self._session.get(IncidentRow, incident.id)
            current_version = existing.version if existing else 0
            raise OptimisticLockError(str(incident.id), current_version)
        await self._session.commit()
        return _row_to_domain(row)

    async def soft_delete(self, incident_id: UUID) -> Incident | None:
        stmt = select(IncidentRow).where(IncidentRow.id == incident_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        if row.deleted_at is not None:
            return _row_to_domain(row)
        row.deleted_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(row)
        return _row_to_domain(row)

    async def list_incidents(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        category: Category | None = None,
        severity: Severity | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Incident], int]:
        base = select(IncidentRow).where(IncidentRow.deleted_at.is_(None))

        if category:
            base = base.where(IncidentRow.category == category.value)
        if severity:
            base = base.where(IncidentRow.severity == severity.value)
        if keyword:
            # Escape ILIKE wildcards (% and _) to prevent pattern injection
            escaped_keyword = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped_keyword}%"
            base = base.where(
                or_(
                    IncidentRow.title.ilike(pattern, escape="\\"),
                    IncidentRow.anti_pattern.ilike(pattern, escape="\\"),
                    IncidentRow.remediation.ilike(pattern, escape="\\"),
                )
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        offset = (page - 1) * per_page
        items_stmt = base.order_by(IncidentRow.created_at.desc()).offset(offset).limit(per_page)
        items_result = await self._session.execute(items_stmt)
        rows = items_result.scalars().all()

        return [_row_to_domain(r) for r in rows], total
