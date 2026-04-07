"""End-to-end integration tests for Product Releases Notification (Phase 5)."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.firebase.auth import get_firebase_token_data
from src.domain.models import Release
from src.main import app

_USER_ID = UUID("00000000-0000-0000-0000-000000000002")
_TOKEN_DATA = {
    "sub": str(_USER_ID),
    "email": "integration@example.com",
    "email_verified": True,
}


@pytest.fixture
async def auth_client() -> AsyncClient:
    """AsyncClient with authenticated Firebase token for integration tests."""
    app.dependency_overrides[get_firebase_token_data] = lambda: _TOKEN_DATA
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_release_notification_flow(
    auth_client: AsyncClient, db_session: AsyncSession
):
    """Test complete flow: badge → dropdown → detail → mark-as-read."""
    from src.adapters.postgres.release_repository import ReleaseRepository

    # 1. Create test releases
    release_repo = ReleaseRepository(db_session)
    release1 = Release(
        id=uuid4(),
        title="v1.0.0",
        version="1.0.0",
        published_date=datetime.now(UTC),
        summary="First release",
        changelog_html="<h1>Features</h1><p>Initial</p>",
        breaking_changes_flag=False,
        documentation_url="https://example.com/v1.0.0",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    release1 = await release_repo.create(release1)
    await db_session.commit()

    # 2. Check unread count
    response = await auth_client.get("/api/v1/releases/unread-count")
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] > 0

    # 3. Get releases list
    response = await auth_client.get("/api/v1/releases")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0

    # 4. Mark as read
    release_id = data["items"][0]["release"]["id"]
    response = await auth_client.patch(f"/api/v1/releases/{release_id}/status")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["is_read"] is True

    # 5. Verify unread count decreased
    response = await auth_client.get("/api/v1/releases/unread-count")
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 0
