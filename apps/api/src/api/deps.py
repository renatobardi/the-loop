"""Shared FastAPI dependencies for dependency injection."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.firebase.auth import get_current_user, get_firebase_token_data
from src.adapters.postgres.action_item_repository import PostgresActionItemRepository
from src.adapters.postgres.attachment_repository import PostgresAttachmentRepository
from src.adapters.postgres.postmortem_repository import PostgresPostmortumRepository
from src.adapters.postgres.repository import PostgresIncidentRepository
from src.adapters.postgres.responder_repository import PostgresResponderRepository
from src.adapters.postgres.session import get_async_session
from src.adapters.postgres.timeline_event_repository import PostgresTimelineEventRepository
from src.domain.services import (
    ActionItemService,
    AttachmentService,
    IncidentService,
    PostmortumService,
    ResponderService,
    TimelineEventService,
)

if TYPE_CHECKING:
    from src.adapters.postgres.analytics_repository import PostgresAnalyticsRepository
    from src.adapters.postgres.cache import RuleVersionCache
    from src.adapters.postgres.rule_version_repository import PostgresRuleVersionRepository
    from src.adapters.postgres.user_repository import PostgresUserRepository
    from src.domain.services import AnalyticsService, RuleVersionService, UserService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresIncidentRepository:
    return PostgresIncidentRepository(session)


def get_postmortem_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresPostmortumRepository:
    return PostgresPostmortumRepository(session)


def get_incident_service(
    repo: PostgresIncidentRepository = Depends(get_repository),
    postmortem_repo: PostgresPostmortumRepository = Depends(get_postmortem_repository),
) -> IncidentService:
    return IncidentService(repo, postmortem_repo)


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


def get_postmortem_service(
    repo: PostgresPostmortumRepository = Depends(get_postmortem_repository),
) -> PostmortumService:
    return PostmortumService(repo)


# ─── Phase B: API Integration & Versioning ───────────────────────────────────


def get_rule_version_repository(
    session: AsyncSession = Depends(get_session),
) -> "PostgresRuleVersionRepository":  # noqa: UP037
    from src.adapters.postgres.rule_version_repository import PostgresRuleVersionRepository

    return PostgresRuleVersionRepository(session)


def get_rule_version_service(
    repo: "PostgresRuleVersionRepository" = Depends(get_rule_version_repository),  # noqa: UP037
) -> "RuleVersionService":  # noqa: UP037
    from src.domain.services import RuleVersionService

    return RuleVersionService(repo)


# ─── Phase C.2: Analytics ────────────────────────────────────────────────────


def get_analytics_repository(
    session: AsyncSession = Depends(get_session),
) -> "PostgresAnalyticsRepository":  # noqa: UP037
    from src.adapters.postgres.analytics_repository import PostgresAnalyticsRepository

    return PostgresAnalyticsRepository(session)


def get_analytics_service(
    repo: "PostgresAnalyticsRepository" = Depends(get_analytics_repository),  # noqa: UP037
) -> "AnalyticsService":  # noqa: UP037
    from src.domain.services import AnalyticsService

    return AnalyticsService(repo)


# Global cache singleton (initialized once at startup)
_rule_version_cache_instance: "RuleVersionCache | None" = None  # noqa: UP037


def init_rule_version_cache() -> None:
    """Initialize the global rule version cache (call in app startup)."""
    global _rule_version_cache_instance
    from src.adapters.postgres.cache import RuleVersionCache

    if _rule_version_cache_instance is None:
        _rule_version_cache_instance = RuleVersionCache(ttl_seconds=300)


def get_rule_version_cache() -> "RuleVersionCache":  # noqa: UP037
    """Get the singleton rule version cache instance."""
    global _rule_version_cache_instance
    if _rule_version_cache_instance is None:
        init_rule_version_cache()
    assert _rule_version_cache_instance is not None, "Cache initialization failed"
    return _rule_version_cache_instance


# ─── Phase 2: Navigation, Dashboard & User Profile ───────────────────────────


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> "PostgresUserRepository":  # noqa: UP037
    from src.adapters.postgres.user_repository import PostgresUserRepository

    return PostgresUserRepository(session)


def get_user_service(
    repo: "PostgresUserRepository" = Depends(get_user_repository),  # noqa: UP037
) -> "UserService":  # noqa: UP037
    from src.domain.services import UserService

    return UserService(repo)


# Re-export get_firebase_token_data for routes that need full token data
__all__ = ["get_firebase_token_data"]
