"""API routes for rule versioning — Phase B integration."""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.adapters.postgres.cache import RuleVersionCache
from src.api.models.rules import (
    PublishRulesRequest,
    PublishRulesResponse,
    RuleVersionResponse,
    VersionListResponse,
    VersionSummary,
)
from src.domain.exceptions import (
    InvalidVersionFormatError,
    RuleVersionNotFoundError,
    VersionAlreadyExistsError,
)
from src.domain.models import RuleVersion
from src.domain.services import RuleVersionService

router = APIRouter(prefix="/api/v1", tags=["rules"])
limiter = Limiter(key_func=get_remote_address)


def _rule_version_to_response(rv: RuleVersion) -> RuleVersionResponse:
    """Convert domain model to API response."""
    return RuleVersionResponse(
        version=rv.version,
        rules_count=rv.rules_count,
        created_at=rv.created_at,
        status=rv.status.value,
        rules=[
            {
                "id": r.id,
                "languages": r.languages,
                "message": r.message,
                "severity": r.severity,
                "metadata": r.metadata,
                "patterns": r.patterns,
            }
            for r in rv.rules
        ],
        published_by=str(rv.published_by) if rv.published_by else None,
        notes=rv.notes,
        deprecated_at=rv.deprecated_at,
    )


@router.get("/rules/latest", response_model=RuleVersionResponse)
@limiter.limit("60/minute")
async def get_latest_rules(
    request: Request,
    service: RuleVersionService = Depends(lambda: None),  # Injected below
    cache: RuleVersionCache = Depends(lambda: None),  # Injected below
) -> RuleVersionResponse:
    """Get the latest active rule version with caching.

    Returns:
        Latest active rule version or 503 if API unavailable.
    """
    from src.api.deps import get_rule_version_cache, get_rule_version_service

    # Re-inject with proper deps (workaround for circular imports)
    service = get_rule_version_service()
    cache = get_rule_version_cache()

    # Try cache first
    cached = await cache.get_latest()
    if cached:
        return _rule_version_to_response(cached)

    # Fetch from repository
    try:
        rule_version = await service.get_latest_active()
        if not rule_version:
            raise HTTPException(status_code=503, detail="No active rule version found")

        # Cache it
        await cache.set_latest(rule_version)

        # Add Cache-Control header
        request.scope["headers"] = list(request.scope.get("headers", [])) + [
            (b"cache-control", b"public, max-age=300")
        ]

        return _rule_version_to_response(rule_version)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Rules service temporarily unavailable: {str(e)}")


@router.get("/rules/{version}", response_model=RuleVersionResponse)
@limiter.limit("60/minute")
async def get_rules_by_version(
    version: str,
    request: Request,
    service: RuleVersionService = Depends(lambda: None),
) -> RuleVersionResponse:
    """Get a specific rule version by semantic version string.

    Args:
        version: Semantic version (e.g., "0.1.0")

    Returns:
        RuleVersion object or 404 if not found.
    """
    from src.api.deps import get_rule_version_service

    service = get_rule_version_service()

    try:
        rule_version = await service.get_by_version(version)
        if not rule_version:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")

        return _rule_version_to_response(rule_version)
    except RuleVersionNotFoundError:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")


@router.get("/rules/versions", response_model=VersionListResponse)
@limiter.limit("60/minute")
async def list_all_versions(
    request: Request,
    service: RuleVersionService = Depends(lambda: None),
) -> VersionListResponse:
    """List all rule versions (all statuses) in reverse creation order.

    Returns:
        List of rule version summaries.
    """
    from src.api.deps import get_rule_version_service

    service = get_rule_version_service()

    try:
        versions = await service.list_all()
        summaries = [
            VersionSummary(
                version=rv.version,
                status=rv.status.value,
                created_at=rv.created_at,
                rules_count=rv.rules_count,
                deprecated_at=rv.deprecated_at,
            )
            for rv in versions
        ]
        return VersionListResponse(versions=summaries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list versions: {str(e)}")


@router.post("/rules/publish", response_model=PublishRulesResponse, status_code=201)
@limiter.limit("10/minute")
async def publish_rules(
    request: Request,
    body: PublishRulesRequest,
    # TODO: Add admin auth check here
    service: RuleVersionService = Depends(lambda: None),
    cache: RuleVersionCache = Depends(lambda: None),
) -> PublishRulesResponse:
    """Publish a new rule version (admin only).

    Args:
        version: Semantic version (e.g., "0.2.0")
        rules: Array of rule definitions
        notes: Optional release notes

    Returns:
        201 Created with new version details or error status.
    """
    from src.api.deps import get_rule_version_cache, get_rule_version_service

    service = get_rule_version_service()
    cache = get_rule_version_cache()

    # TODO: Check admin auth (require_admin dependency)
    # if not user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin role required")

    try:
        # Validate request
        if not body.version or not body.rules:
            raise HTTPException(status_code=400, detail="version and rules are required")

        # Convert request rules to dict format
        rules_json = [
            {
                "id": r.id,
                "languages": r.languages,
                "message": r.message,
                "severity": r.severity,
                "metadata": r.metadata,
                "patterns": r.patterns,
            }
            for r in body.rules
        ]

        # Publish version
        new_version = await service.publish_version(
            version=body.version,
            rules_json=rules_json,
            published_by=UUID("00000000-0000-0000-0000-000000000000"),  # TODO: Get from auth
            notes=body.notes,
        )

        # Invalidate cache
        await cache.invalidate()

        return PublishRulesResponse(
            message=f"Published {new_version.version} with {new_version.rules_count} rules",
            version=new_version.version,
            created_at=new_version.created_at,
            rules_count=new_version.rules_count,
        )

    except InvalidVersionFormatError as e:
        raise HTTPException(status_code=400, detail=f"Invalid version format: {e}")
    except VersionAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=f"Version conflict: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish version: {str(e)}")
