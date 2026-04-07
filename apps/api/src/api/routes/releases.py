"""API routes for Product Releases Notification (Phase 5)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as http_status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.firebase.auth import get_current_user
from src.adapters.postgres.notification_repository import (
    ReleaseNotificationStatusRepository,
)
from src.adapters.postgres.release_repository import ReleaseRepository
from src.api.deps import get_session
from src.api.middleware import limiter
from src.domain.exceptions import ReleaseNotFoundError
from src.domain.models import Release, ReleaseNotificationStatus
from src.domain.services import ReleaseNotificationService

router = APIRouter(prefix="/api/v1/releases", tags=["releases"])


class ReleaseResponse(BaseModel):
    """Response model for Release."""

    id: UUID
    title: str
    version: str
    published_date: str
    summary: str | None = None
    changelog_html: str | None = None
    breaking_changes_flag: bool = False
    documentation_url: str | None = None

    @classmethod
    def from_domain(cls, release: Release) -> "ReleaseResponse":
        return cls(
            id=release.id,
            title=release.title,
            version=release.version,
            published_date=release.published_date.isoformat(),
            summary=release.summary,
            changelog_html=release.changelog_html,
            breaking_changes_flag=release.breaking_changes_flag,
            documentation_url=release.documentation_url,
        )


class ReleaseWithStatusResponse(BaseModel):
    """Response model for Release with read status."""

    release: ReleaseResponse
    is_read: bool
    read_at: str | None = None

    @classmethod
    def from_domain(
        cls, release: Release, status: ReleaseNotificationStatus | None
    ) -> "ReleaseWithStatusResponse":
        return cls(
            release=ReleaseResponse.from_domain(release),
            is_read=status.is_read if status else False,
            read_at=status.read_at.isoformat() if status and status.read_at else None,
        )


class ReleasesListResponse(BaseModel):
    """Response model for releases list."""

    items: list[ReleaseWithStatusResponse]
    total: int


class ReleaseNotificationStatusResponse(BaseModel):
    """Response model for release notification status."""

    id: UUID
    release_id: UUID
    user_id: UUID
    is_read: bool
    read_at: str | None = None

    @classmethod
    def from_domain(cls, status: ReleaseNotificationStatus) -> "ReleaseNotificationStatusResponse":
        return cls(
            id=status.id,
            release_id=status.release_id,
            user_id=status.user_id,
            is_read=status.is_read,
            read_at=status.read_at.isoformat() if status.read_at else None,
        )


async def get_release_service(
    session: AsyncSession = Depends(get_session),
) -> ReleaseNotificationService:
    """Dependency: inject ReleaseNotificationService with repositories."""
    release_repo = ReleaseRepository(session)
    notification_repo = ReleaseNotificationStatusRepository(session)
    return ReleaseNotificationService(release_repo, notification_repo)


@router.get("", response_model=ReleasesListResponse)
@limiter.limit("60/minute")
async def get_releases(
    request: Request,
    current_user: UUID = Depends(get_current_user),
    service: ReleaseNotificationService = Depends(get_release_service),
) -> ReleasesListResponse:
    """Get recent releases with read status for authenticated user."""
    results = await service.get_unread_releases(current_user, limit=10)
    items = [
        ReleaseWithStatusResponse.from_domain(release, status)
        for release, status in results
    ]
    return ReleasesListResponse(items=items, total=len(items))


@router.get("/unread-count", response_model=dict[str, int])
@limiter.limit("120/minute")
async def get_unread_count(
    request: Request,
    current_user: UUID = Depends(get_current_user),
    service: ReleaseNotificationService = Depends(get_release_service),
) -> dict[str, int]:
    """Get count of unread releases for authenticated user."""
    count = await service.get_unread_count(current_user)
    return {"unread_count": count}


@router.patch("/{release_id}/status", response_model=ReleaseNotificationStatusResponse)
@limiter.limit("60/minute")
async def mark_release_as_read(
    request: Request,
    release_id: UUID,
    current_user: UUID = Depends(get_current_user),
    service: ReleaseNotificationService = Depends(get_release_service),
) -> ReleaseNotificationStatusResponse:
    """Mark a release as read for the authenticated user."""
    try:
        notification_status = await service.mark_as_read(current_user, release_id)
        return ReleaseNotificationStatusResponse.from_domain(notification_status)
    except ReleaseNotFoundError as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get("/{release_id}", response_model=ReleaseResponse)
@limiter.limit("60/minute")
async def get_release_detail(
    request: Request,
    release_id: UUID,
    current_user: UUID = Depends(get_current_user),
    service: ReleaseNotificationService = Depends(get_release_service),
) -> ReleaseResponse:
    """Get full details for a specific release."""
    try:
        release = await service.get_release_detail(release_id)
        return ReleaseResponse.from_domain(release)
    except ReleaseNotFoundError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e)) from e
