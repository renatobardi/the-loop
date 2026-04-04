"""PostgreSQL adapter implementing ScanRepoPort."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import ApiKeyRow, ScanFindingRow, ScanRow
from src.domain.models import Scan


def _row_to_domain(row: ScanRow) -> Scan:
    return Scan(
        id=row.id,
        api_key_id=row.api_key_id,
        repository=row.repository,
        branch=row.branch,
        pr_number=row.pr_number,
        rules_version=row.rules_version,
        findings_count=row.findings_count,
        errors_count=row.errors_count,
        warnings_count=row.warnings_count,
        duration_ms=row.duration_ms,
        created_at=row.created_at,
    )


class PostgresScanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_with_findings(
        self,
        api_key_id: UUID,
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
        now = datetime.now(UTC)
        scan_id = uuid.uuid4()
        scan_row = ScanRow(
            id=scan_id,
            api_key_id=api_key_id,
            repository=repository,
            branch=branch,
            pr_number=pr_number,
            rules_version=rules_version,
            findings_count=findings_count,
            errors_count=errors_count,
            warnings_count=warnings_count,
            duration_ms=duration_ms,
            created_at=now,
        )
        self._session.add(scan_row)
        await self._session.flush()

        for finding in findings:
            finding_row = ScanFindingRow(
                id=uuid.uuid4(),
                scan_id=scan_id,
                rule_id=str(finding.get("rule_id", "")),
                file_path=str(finding.get("file_path", "")),
                line_number=int(finding.get("line_number", 0)),
                severity=str(finding.get("severity", "")),
                created_at=now,
            )
            self._session.add(finding_row)

        await self._session.flush()
        await self._session.commit()
        return _row_to_domain(scan_row)

    async def list_by_owner(self, owner_id: UUID, limit: int = 50) -> list[Scan]:
        # Join scans → api_keys, filter by owner_id
        stmt = (
            select(ScanRow)
            .join(ApiKeyRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ApiKeyRow.owner_id == owner_id)
            .order_by(ScanRow.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_row_to_domain(row) for row in result.scalars().all()]

    async def get_summary(self, owner_id: UUID) -> dict[str, object]:
        # Total scans
        count_stmt = (
            select(func.count(ScanRow.id))
            .join(ApiKeyRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ApiKeyRow.owner_id == owner_id)
        )
        total_result = await self._session.execute(count_stmt)
        total_scans = total_result.scalar_one() or 0

        # Total findings
        findings_stmt = (
            select(func.sum(ScanRow.findings_count))
            .join(ApiKeyRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ApiKeyRow.owner_id == owner_id)
        )
        findings_result = await self._session.execute(findings_stmt)
        total_findings = findings_result.scalar_one() or 0

        # Scans by week (last 12 weeks)
        scans_by_week_stmt = (
            select(ScanRow)
            .join(ApiKeyRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ApiKeyRow.owner_id == owner_id)
            .order_by(ScanRow.created_at.desc())
            .limit(200)
        )
        scans_result = await self._session.execute(scans_by_week_stmt)
        scans_rows = scans_result.scalars().all()

        week_map: dict[str, dict[str, int]] = {}
        for row in scans_rows:
            iso = row.created_at.isocalendar()
            week_key = f"{iso.year}-W{iso.week:02d}"
            if week_key not in week_map:
                week_map[week_key] = {"count": 0, "findings": 0}
            week_map[week_key]["count"] += 1
            week_map[week_key]["findings"] += row.findings_count

        scans_by_week: list[dict[str, object]] = [
            {"week": week, "count": data["count"], "findings": data["findings"]}
            for week, data in sorted(week_map.items())
        ]

        # Top rules from scan_findings
        top_rules_stmt = (
            select(ScanFindingRow.rule_id, func.count(ScanFindingRow.id).label("cnt"))
            .join(ScanRow, ScanFindingRow.scan_id == ScanRow.id)
            .join(ApiKeyRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ApiKeyRow.owner_id == owner_id)
            .group_by(ScanFindingRow.rule_id)
            .order_by(func.count(ScanFindingRow.id).desc())
            .limit(10)
        )
        top_rules_result = await self._session.execute(top_rules_stmt)
        top_rules: list[dict[str, object]] = [
            {"rule_id": row.rule_id, "count": row.cnt} for row in top_rules_result.all()
        ]

        # Distinct repositories scanned by this user
        repos_stmt = (
            select(func.count(func.distinct(ScanRow.repository)))
            .join(ApiKeyRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ApiKeyRow.owner_id == owner_id)
        )
        repos_result = await self._session.execute(repos_stmt)
        active_repos = repos_result.scalar_one() or 0

        return {
            "total_scans": total_scans,
            "total_findings": int(total_findings),
            "active_repos": int(active_repos),
            "scans_by_week": scans_by_week,
            "top_rules": top_rules,
        }

    async def get_global_metrics(self) -> dict[str, object]:
        """Admin-only: global scan metrics across all users."""
        from datetime import timedelta

        # Active repos: distinct owner_id with scans in last 30 days
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        active_repos_stmt = (
            select(func.count(func.distinct(ApiKeyRow.owner_id)))
            .join(ScanRow, ScanRow.api_key_id == ApiKeyRow.id)
            .where(ScanRow.created_at >= thirty_days_ago)
        )
        active_repos_result = await self._session.execute(active_repos_stmt)
        active_repos = active_repos_result.scalar_one() or 0

        # Scans by week (global, last 200)
        scans_by_week_stmt = (
            select(ScanRow)
            .order_by(ScanRow.created_at.desc())
            .limit(200)
        )
        scans_result = await self._session.execute(scans_by_week_stmt)
        scans_rows = scans_result.scalars().all()

        week_map: dict[str, dict[str, int]] = {}
        for row in scans_rows:
            iso = row.created_at.isocalendar()
            week_key = f"{iso.year}-W{iso.week:02d}"
            if week_key not in week_map:
                week_map[week_key] = {"count": 0, "findings": 0}
            week_map[week_key]["count"] += 1
            week_map[week_key]["findings"] += row.findings_count

        scans_by_week: list[dict[str, object]] = [
            {"week": week, "count": data["count"], "findings": data["findings"]}
            for week, data in sorted(week_map.items())
        ]

        # Top languages from rule_id prefix
        top_rules_stmt = (
            select(ScanFindingRow.rule_id, func.count(ScanFindingRow.id).label("cnt"))
            .group_by(ScanFindingRow.rule_id)
            .order_by(func.count(ScanFindingRow.id).desc())
            .limit(100)
        )
        top_rules_result = await self._session.execute(top_rules_stmt)
        lang_map: dict[str, int] = {}
        for rule_id_val, cnt_val in top_rules_result.all():
            rule_id: str = str(rule_id_val or "")
            if rule_id.startswith("js-") or rule_id.startswith("ts-"):
                lang = "JS/TS"
            elif rule_id.startswith("go-"):
                lang = "Go"
            else:
                lang = "Python"
            lang_map[lang] = lang_map.get(lang, 0) + int(cnt_val)

        top_languages: list[dict[str, object]] = [
            {"language": lang, "count": count}
            for lang, count in sorted(lang_map.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "active_repos": int(active_repos),
            "scans_by_week": scans_by_week,
            "top_languages": top_languages,
        }
