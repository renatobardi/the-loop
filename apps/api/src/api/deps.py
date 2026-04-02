"""Shared FastAPI dependencies for dependency injection."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.firebase.auth import get_current_user
from src.adapters.postgres.repository import PostgresIncidentRepository
from src.adapters.postgres.session import get_async_session
from src.adapters.postgres.timeline_event_repository import PostgresTimelineEventRepository
from src.domain.services import IncidentService, TimelineEventService


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
