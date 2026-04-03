"""Shared FastAPI dependencies for dependency injection."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.firebase.auth import get_current_user
from src.adapters.postgres.action_item_repository import PostgresActionItemRepository
from src.adapters.postgres.attachment_repository import PostgresAttachmentRepository
from src.adapters.postgres.repository import PostgresIncidentRepository
from src.adapters.postgres.responder_repository import PostgresResponderRepository
from src.adapters.postgres.session import get_async_session
from src.adapters.postgres.timeline_event_repository import PostgresTimelineEventRepository
from src.domain.services import (
    ActionItemService,
    AttachmentService,
    IncidentService,
    ResponderService,
    TimelineEventService,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresIncidentRepository:
    return PostgresIncidentRepository(session)


def get_incident_service(
    repo: PostgresIncidentRepository = Depends(get_repository),
) -> IncidentService:
    return IncidentService(repo)


def get_authenticated_user(
    user_id: UUID = Depends(get_current_user),
) -> UUID:
    return user_id


def get_timeline_event_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresTimelineEventRepository:
    return PostgresTimelineEventRepository(session)


def get_timeline_event_service(
    repo: PostgresTimelineEventRepository = Depends(get_timeline_event_repository),
) -> TimelineEventService:
    return TimelineEventService(repo)


def get_responder_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresResponderRepository:
    return PostgresResponderRepository(session)


def get_responder_service(
    repo: PostgresResponderRepository = Depends(get_responder_repository),
) -> ResponderService:
    return ResponderService(repo)


def get_action_item_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresActionItemRepository:
    return PostgresActionItemRepository(session)


def get_action_item_service(
    repo: PostgresActionItemRepository = Depends(get_action_item_repository),
) -> ActionItemService:
    return ActionItemService(repo)


def get_attachment_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresAttachmentRepository:
    return PostgresAttachmentRepository(session)


def get_attachment_service(
    repo: PostgresAttachmentRepository = Depends(get_attachment_repository),
) -> AttachmentService:
    return AttachmentService(repo)


# ─── Phase B: API Integration & Versioning ───────────────────────────────────


def get_rule_version_repository(
    session: AsyncSession = Depends(get_session),
):
    from src.adapters.postgres.rule_version_repository import PostgresRuleVersionRepository

    return PostgresRuleVersionRepository(session)


def get_rule_version_service(
    repo=Depends(get_rule_version_repository),
):
    from src.domain.services import RuleVersionService

    return RuleVersionService(repo)


# Global cache singleton (initialized once at startup)
_rule_version_cache_instance = None


def init_rule_version_cache() -> None:
    """Initialize the global rule version cache (call in app startup)."""
    global _rule_version_cache_instance
    from src.adapters.postgres.cache import RuleVersionCache

    if _rule_version_cache_instance is None:
        _rule_version_cache_instance = RuleVersionCache(ttl_seconds=300)


def get_rule_version_cache():
    """Get the singleton rule version cache instance."""
    global _rule_version_cache_instance
    if _rule_version_cache_instance is None:
        init_rule_version_cache()
    return _rule_version_cache_instance
