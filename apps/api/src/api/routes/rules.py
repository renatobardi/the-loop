"""API routes for rule versioning — Phase B integration."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from src.adapters.firebase.auth import get_current_user
from src.adapters.postgres.cache import RuleVersionCache
from src.api.deps import get_rule_version_cache, get_rule_version_service
from src.api.middleware import limiter
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


def _rule_version_to_response(rv: RuleVersion) -> dict[str, Any]:
    """Convert domain model to API response dict."""
    return {
        "version": rv.version,
        "rules_count": rv.rules_count,
        "created_at": rv.created_at,
        "status": rv.status.value,
        "rules": [
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
        "published_by": str(rv.published_by) if rv.published_by else None,
        "notes": rv.notes,
        "deprecated_at": rv.deprecated_at,
    }


@router.get("/rules/latest", response_model=RuleVersionResponse)
@limiter.limit("60/minute")
async def get_latest_rules(
    request: Request,
    service: RuleVersionService = Depends(get_rule_version_service),
    cache: RuleVersionCache = Depends(get_rule_version_cache),
) -> JSONResponse:
    """Get the latest active rule version with caching.

    Returns:
        200: Latest active rule version with Cache-Control header
        503: No active rule version or service unavailable
    """
    try:
        # Try cache first
        cached = await cache.get_latest()
        if cached:
            response_data = _rule_version_to_response(cached)
            return JSONResponse(
                content=response_data,
                headers={"Cache-Control": "public, max-age=300"},
            )

        # Fetch from repository
        rule_version = await service.get_latest_active()
        if not rule_version:
            raise HTTPException(status_code=503, detail="No active rule version found")

        # Cache it
        await cache.set_latest(rule_version)

        response_data = _rule_version_to_response(rule_version)
        return JSONResponse(
            content=response_data,
            headers={"Cache-Control": "public, max-age=300"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Rules service temporarily unavailable: {e!s}",
        ) from e


@router.get("/rules/versions", response_model=VersionListResponse)
@limiter.limit("60/minute")
async def list_all_versions(
    request: Request,
    service: RuleVersionService = Depends(get_rule_version_service),
) -> VersionListResponse:
    """List all rule versions (all statuses) in reverse creation order.

    Returns:
        200: List of rule version summaries
        500: Server error
    """
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
        raise HTTPException(status_code=500, detail=f"Failed to list versions: {e!s}") from e


@router.get("/rules/{version}", response_model=RuleVersionResponse)
@limiter.limit("60/minute")
async def get_rules_by_version(
    version: str,
    request: Request,
    service: RuleVersionService = Depends(get_rule_version_service),
) -> RuleVersionResponse:
    """Get a specific rule version by semantic version string.

    Args:
        version: Semantic version (e.g., "0.1.0")

    Returns:
        200: Rule version object (any status)
        404: Version not found
    """
    try:
        rule_version = await service.get_by_version(version)
        if not rule_version:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")

        return RuleVersionResponse(**_rule_version_to_response(rule_version))
    except RuleVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Version {version} not found") from e


@router.post("/rules/publish", response_model=PublishRulesResponse, status_code=201)
@limiter.limit("10/minute")
async def publish_rules(
    request: Request,
    body: PublishRulesRequest,
    user_id: UUID = Depends(get_current_user),
    service: RuleVersionService = Depends(get_rule_version_service),
    cache: RuleVersionCache = Depends(get_rule_version_cache),
) -> PublishRulesResponse:
    """Publish a new rule version (admin only).

    Args:
        version: Semantic version (e.g., "0.2.0")
        rules: Array of rule definitions
        notes: Optional release notes

    Returns:
        201: Created with new version details
        400: Invalid version format or missing required fields
        403: User is not admin
        409: Version already exists
        500: Server error
    """
    # Check admin auth (TODO: implement proper admin role check)
    # For now, allow any authenticated user to publish
    # Future: Check if user.is_admin from Firebase claims
    if not user_id:
        raise HTTPException(status_code=403, detail="Admin role required")

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
            published_by=user_id,
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
        raise HTTPException(status_code=400, detail=f"Invalid version format: {e}") from e
    except VersionAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=f"Version conflict: {e}") from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish version: {e!s}") from e
