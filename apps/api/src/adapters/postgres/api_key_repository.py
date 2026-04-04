"""PostgreSQL adapter implementing ApiKeyRepoPort."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import ApiKeyRow, RuleWhitelistRow
from src.domain.exceptions import ApiKeyNotFoundError
from src.domain.models import ApiKey


def _row_to_domain(row: ApiKeyRow) -> ApiKey:
    return ApiKey(
        id=row.id,
        owner_id=row.owner_id,
        name=row.name,
        prefix=row.prefix,
        last_used_at=row.last_used_at,
        revoked_at=row.revoked_at,
        created_at=row.created_at,
    )


class PostgresApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, owner_id: UUID, name: str, key_hash: str, prefix: str) -> ApiKey:
        now = datetime.now(UTC)
        row = ApiKeyRow(
            id=uuid.uuid4(),
            owner_id=owner_id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            last_used_at=None,
            revoked_at=None,
            created_at=now,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.commit()
        return _row_to_domain(row)

    async def get_by_hash(self, key_hash: str) -> ApiKey | None:
        stmt = select(ApiKeyRow).where(ApiKeyRow.key_hash == key_hash)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _row_to_domain(row) if row is not None else None

    async def list_by_owner(self, owner_id: UUID) -> list[ApiKey]:
        stmt = (
            select(ApiKeyRow)
            .where(ApiKeyRow.owner_id == owner_id)
            .order_by(ApiKeyRow.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [_row_to_domain(row) for row in result.scalars().all()]

    async def revoke(self, key_id: UUID, owner_id: UUID) -> ApiKey:
        row = await self._session.get(ApiKeyRow, key_id)
        if row is None or row.owner_id != owner_id:
            raise ApiKeyNotFoundError(str(key_id))
        row.revoked_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.commit()
        return _row_to_domain(row)

    async def mark_used(self, key_id: UUID) -> None:
        row = await self._session.get(ApiKeyRow, key_id)
        if row is not None:
            row.last_used_at = datetime.now(UTC)
            await self._session.flush()
            await self._session.commit()

    async def get_whitelist(self, key_id: UUID) -> list[str]:
        stmt = select(RuleWhitelistRow).where(RuleWhitelistRow.api_key_id == key_id)
        result = await self._session.execute(stmt)
        return [row.rule_id for row in result.scalars().all()]

    async def add_to_whitelist(self, key_id: UUID, rule_id: str) -> None:
        row = RuleWhitelistRow(
            id=uuid.uuid4(),
            api_key_id=key_id,
            rule_id=rule_id,
            created_at=datetime.now(UTC),
        )
        try:
            self._session.add(row)
            await self._session.flush()
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            # Already whitelisted — silently ignore duplicate

    async def remove_from_whitelist(self, key_id: UUID, rule_id: str) -> None:
        stmt = select(RuleWhitelistRow).where(
            RuleWhitelistRow.api_key_id == key_id,
            RuleWhitelistRow.rule_id == rule_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is not None:
            await self._session.delete(row)
            await self._session.flush()
            await self._session.commit()
