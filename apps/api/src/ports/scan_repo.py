"""Port interface for scan persistence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import Scan


class ScanRepoPort(Protocol):
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
    ) -> Scan: ...

    async def list_by_owner(self, owner_id: UUID, limit: int = 50) -> list[Scan]: ...

    async def get_summary(self, owner_id: UUID) -> dict[str, object]: ...

    async def get_global_metrics(self) -> dict[str, object]: ...
