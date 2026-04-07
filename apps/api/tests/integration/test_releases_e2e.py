"""End-to-end integration tests for Product Releases Notification (Phase 5)."""

from datetime import UTC, datetime
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.domain.models import Release


@pytest.mark.asyncio
async def test_release_notification_flow(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
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
    response = await client.get("/api/v1/releases/unread-count", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] > 0

    # 3. Get releases list
    response = await client.get("/api/v1/releases", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0

    # 4. Mark as read
    release_id = data["items"][0]["release"]["id"]
    response = await client.patch(
        f"/api/v1/releases/{release_id}/status",
        headers=auth_headers
    )
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["is_read"] is True

    # 5. Verify unread count decreased
    response = await client.get("/api/v1/releases/unread-count", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["unread_count"] == 0
