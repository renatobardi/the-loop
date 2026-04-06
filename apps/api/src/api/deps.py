"""Shared FastAPI dependencies for dependency injection."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
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
    ApiKeyService,
    AttachmentService,
    IncidentService,
    PostmortumService,
    ReleaseNotificationService,
    ResponderService,
    ScanService,
    TimelineEventService,
)

if TYPE_CHECKING:
    from src.adapters.firebase.auth import FirebaseTokenData
    from src.adapters.postgres.analytics_cache import AnalyticsCache
    from src.adapters.postgres.analytics_repository import PostgresAnalyticsRepository
    from src.adapters.postgres.api_key_repository import PostgresApiKeyRepository
    from src.adapters.postgres.cache import RuleVersionCache
    from src.adapters.postgres.rule_version_repository import PostgresRuleVersionRepository
    from src.adapters.postgres.scan_repository import PostgresScanRepository
    from src.adapters.postgres.user_repository import PostgresUserRepository
    from src.domain.models import ApiKey
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


# Analytics cache singleton — 5-minute TTL, shared across all requests
_analytics_cache_instance: "AnalyticsCache | None" = None  # noqa: UP037


def get_analytics_cache() -> "AnalyticsCache":  # noqa: UP037
    from src.adapters.postgres.analytics_cache import AnalyticsCache

    global _analytics_cache_instance
    if _analytics_cache_instance is None:
        _analytics_cache_instance = AnalyticsCache()
    return _analytics_cache_instance


def get_analytics_service(
    repo: "PostgresAnalyticsRepository" = Depends(get_analytics_repository),  # noqa: UP037
    cache: "AnalyticsCache" = Depends(get_analytics_cache),  # noqa: UP037
) -> "AnalyticsService":  # noqa: UP037
    from src.domain.services import AnalyticsService

    return AnalyticsService(repo, cache)


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


# ─── Phase 4: Semgrep Platform — API Keys & Scans ────────────────────────────


class ApiKeyContext:
    """Holds a validated API key and its associated rule whitelist."""

    def __init__(self, api_key: ApiKey, whitelist: list[str]) -> None:
        self.api_key = api_key
        self.whitelist = whitelist


def get_api_key_repository(
    session: AsyncSession = Depends(get_session),
) -> "PostgresApiKeyRepository":  # noqa: UP037
    from src.adapters.postgres.api_key_repository import PostgresApiKeyRepository

    return PostgresApiKeyRepository(session)


def get_api_key_service(
    repo: "PostgresApiKeyRepository" = Depends(get_api_key_repository),  # noqa: UP037
) -> ApiKeyService:
    return ApiKeyService(repo)


def get_scan_repository(
    session: AsyncSession = Depends(get_session),
) -> "PostgresScanRepository":  # noqa: UP037
    from src.adapters.postgres.scan_repository import PostgresScanRepository

    return PostgresScanRepository(session)


def get_scan_service(
    repo: "PostgresScanRepository" = Depends(get_scan_repository),  # noqa: UP037
    api_key_repo: "PostgresApiKeyRepository" = Depends(get_api_key_repository),  # noqa: UP037
) -> ScanService:
    return ScanService(repo, api_key_repo)


async def get_optional_identity(
    request: Request,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> "FirebaseTokenData | ApiKeyContext | None":  # noqa: UP037
    """Detect caller identity from Authorization header (non-mandatory).

    Returns:
        - None if no Authorization header (anonymous)
        - ApiKeyContext(api_key, whitelist) if Bearer token starts with "tlp_"
        - FirebaseTokenData if Bearer token is a Firebase JWT ("eyJ..." prefix)
    """
    from src.domain.exceptions import ApiKeyInvalidError, ApiKeyRevokedError

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").strip()
    if token.startswith("tlp_"):
        try:
            api_key = await api_key_service.validate(token)
            whitelist = await api_key_service.get_whitelist(api_key.id)
            return ApiKeyContext(api_key=api_key, whitelist=whitelist)
        except (ApiKeyInvalidError, ApiKeyRevokedError):
            return None

    if token.startswith("eyJ"):
        # Firebase JWT — verify and return token data
        from src.adapters.firebase.auth import FirebaseTokenData, _uid_to_uuid, verify_token

        decoded = verify_token(token)
        uid: str = decoded.get("uid", "")
        return FirebaseTokenData(
            user_id=_uid_to_uuid(uid),
            firebase_uid=uid,
            email=decoded.get("email", ""),
            display_name=decoded.get("name") or None,
        )

    return None


async def require_admin(
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    user_service: UserService = Depends(get_user_service),
) -> FirebaseTokenData:
    """Require Firebase auth + is_admin == True on the user record."""

    user = await user_service.get_or_create(
        firebase_uid=token_data["firebase_uid"],
        email=token_data["email"],
        display_name=token_data["display_name"],
    )
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return token_data


# Re-export get_firebase_token_data for routes that need full token data
__all__ = ["get_firebase_token_data", "get_optional_identity"]
