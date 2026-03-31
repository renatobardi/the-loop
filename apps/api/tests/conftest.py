"""Shared test fixtures."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from src.adapters.firebase.auth import get_current_user
from src.main import app

TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def test_user_id() -> UUID:
    return TEST_USER_ID


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: TEST_USER_ID
    yield TestClient(app)  # type: ignore[misc]
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_current_user] = lambda: TEST_USER_ID
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
