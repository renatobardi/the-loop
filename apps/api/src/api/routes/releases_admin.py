"""Admin routes for releases management (Phase 5 - GitHub Integration)."""

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.github.releases_api import GitHubReleasesApiClient
from src.adapters.postgres.release_repository import ReleaseRepository
from src.api.deps import get_session, limiter, require_admin
from src.domain.services import ReleaseSyncService

router = APIRouter(prefix="/api/v1/admin/releases", tags=["admin-releases"])


async def get_release_sync_service(
    session: AsyncSession = Depends(get_session),
) -> ReleaseSyncService:
    """Dependency: inject ReleaseSyncService with repositories."""
    release_repo = ReleaseRepository(session)
    github_token = os.getenv("GITHUB_TOKEN")
    github_client = GitHubReleasesApiClient("renatobardi", "the-loop", token=github_token)
    return ReleaseSyncService(release_repo, github_client)


@router.post("/sync", response_model=dict)
@limiter.limit("10/minute")
async def sync_releases_from_github(
    _admin_token=Depends(require_admin),
    service: ReleaseSyncService = Depends(get_release_sync_service),
) -> dict:
    """Admin endpoint to manually sync releases from GitHub."""
    try:
        count = await service.sync_releases()
        return {
            "status": "success",
            "synced_count": count,
            "message": f"Synced {count} new releases from GitHub"
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
