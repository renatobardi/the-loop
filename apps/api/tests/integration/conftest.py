"""Integration test fixtures — require a real PostgreSQL instance with migrations applied."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from src.config import settings


def _make_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create a sessionmaker backed by a NullPool engine.

    NullPool is critical for integration tests: it never reuses connections, so a broken
    connection from a constraint-violation test cannot contaminate the next test.
    """
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Real DB session, fully rolled back after each test for isolation."""
    factory = _make_session_factory()
    async with factory() as session:
        yield session
        await session.rollback()
