"""API routes for rule versioning — Phase B integration."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.adapters.firebase.auth import FirebaseTokenData
from src.adapters.postgres.cache import RuleVersionCache
from src.api.deps import (
    ApiKeyContext,
    get_optional_identity,
    get_rule_version_cache,
    get_rule_version_service,
    get_scan_service,
    require_admin,
)
from src.api.middleware import limiter
from src.api.models.rules import (
    DeprecateRulesRequest,
    DeprecateRulesResponse,
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
from src.domain.services import RuleVersionService, ScanService

router = APIRouter(prefix="/api/v1", tags=["rules"])


# ─── Admin request/response models ───────────────────────────────────────────


class CreateVersionRequest(BaseModel):
    version: str


class CreateVersionResponse(BaseModel):
    version: str
    status: str


class EditRuleRequest(BaseModel):
    message: str
    severity: str
    pattern: str
    languages: list[str] = ["python"]


def _rule_version_to_response(rv: RuleVersion) -> dict[str, Any]:
    """Convert domain model to API response dict."""
    return {
        "version": rv.version,
        "rules_count": rv.rules_count,
        "created_at": rv.created_at.isoformat(),
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
        "deprecated_at": rv.deprecated_at.isoformat() if rv.deprecated_at else None,
    }


async def _invalidate_rules_cache(
    cache: RuleVersionCache,
) -> None:
    """Invalidate rules cache after publish/deprecate operations."""
    await cache.invalidate()


@router.get("/rules/latest", response_model=RuleVersionResponse)
@limiter.limit("60/minute")
async def get_latest_rules(
    request: Request,
    identity: object = Depends(get_optional_identity),
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
        if cached and cached.rules:
            response_data = _rule_version_to_response(cached)
            # Apply whitelist filtering for API keys (Phase 4 will populate whitelist from DB)
            if isinstance(identity, ApiKeyContext) and identity.whitelist:
                response_data["rules"] = [
                    r for r in response_data["rules"] if r["id"] not in identity.whitelist
                ]
                response_data["rules_count"] = len(response_data["rules"])
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
        # Apply whitelist filtering for API keys (Phase 4 will populate whitelist from DB)
        if isinstance(identity, ApiKeyContext) and identity.whitelist:
            response_data["rules"] = [
                r for r in response_data["rules"] if r["id"] not in identity.whitelist
            ]
            response_data["rules_count"] = len(response_data["rules"])
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


@router.get("/rules/deprecated", response_model=VersionListResponse)
@limiter.limit("60/minute")
async def list_deprecated_versions(
    request: Request,
    service: RuleVersionService = Depends(get_rule_version_service),
) -> VersionListResponse:
    """List all deprecated rule versions (useful for rollback decisions).

    Returns:
        200: List of deprecated version summaries in reverse creation order
        500: Server error
    """
    try:
        versions = await service.list_all()
        # Filter to deprecated only, sorted by created_at DESC
        deprecated = [v for v in versions if v.status.value == "deprecated"]
        summaries = [
            VersionSummary(
                version=rv.version,
                status=rv.status.value,
                created_at=rv.created_at,
                rules_count=rv.rules_count,
                deprecated_at=rv.deprecated_at,
            )
            for rv in deprecated
        ]
        return VersionListResponse(versions=summaries)
    except Exception as e:
        detail = f"Failed to list deprecated versions: {e!s}"
        raise HTTPException(status_code=500, detail=detail) from e


@router.get("/rules/{version}", response_model=RuleVersionResponse)
@limiter.limit("60/minute")
async def get_rules_by_version(
    version: str,
    request: Request,
    identity: object = Depends(get_optional_identity),
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

        rule_version_data = _rule_version_to_response(rule_version)
        # Apply whitelist filtering for API keys (Phase 4 will populate whitelist from DB)
        if isinstance(identity, ApiKeyContext) and identity.whitelist:
            rule_version_data["rules"] = [
                r for r in rule_version_data["rules"] if r["id"] not in identity.whitelist
            ]
            rule_version_data["rules_count"] = len(rule_version_data["rules"])
        return RuleVersionResponse(**rule_version_data)
    except RuleVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Version {version} not found") from e


@router.post("/rules/publish", response_model=PublishRulesResponse, status_code=201)
@limiter.limit("10/minute")
async def publish_rules(
    request: Request,
    body: PublishRulesRequest,
    admin_data: FirebaseTokenData = Depends(require_admin),
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
    user_id = admin_data["user_id"]

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

        # Invalidate cache (shared with deprecate endpoint)
        await _invalidate_rules_cache(cache)

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


@router.post("/rules/deprecate", response_model=DeprecateRulesResponse, status_code=200)
@limiter.limit("10/minute")
async def deprecate_rules_version(
    request: Request,
    body: DeprecateRulesRequest,
    admin_data: FirebaseTokenData = Depends(require_admin),
    service: RuleVersionService = Depends(get_rule_version_service),
    cache: RuleVersionCache = Depends(get_rule_version_cache),
) -> DeprecateRulesResponse:
    """Mark a rule version as deprecated (admin only).

    Useful for marking versions as no longer active when security issues or bugs are found.
    The deprecation takes effect immediately — the next /latest request will return the
    newest non-deprecated version.

    Args:
        version: Semantic version to deprecate (e.g., "0.1.0")

    Returns:
        200: Version marked deprecated with deprecation timestamp
        403: User is not authenticated
        404: Version not found
        500: Server error

    Example:
        ```bash
        curl -X POST https://api.../api/v1/rules/deprecate \\
          -H "Authorization: Bearer $TOKEN" \\
          -d '{"version": "0.1.0"}'
        ```

    Side effects:
        - Marks version.status = "deprecated"
        - Sets version.deprecated_at = now()
        - Invalidates /latest cache immediately
    """
    try:
        # Deprecate version
        deprecated_version = await service.deprecate_version(body.version)

        # Invalidate cache (shared with publish endpoint)
        await _invalidate_rules_cache(cache)

        return DeprecateRulesResponse(
            message=f"Deprecated version {deprecated_version.version}",
            version=deprecated_version.version,
            deprecated_at=deprecated_version.deprecated_at,  # type: ignore[arg-type]
        )

    except RuleVersionNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Version {body.version} not found") from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deprecate version: {e!s}") from e


# ─── Admin-only endpoints (Phases 6 & 7) ─────────────────────────────────────


@router.post("/rules/versions", response_model=CreateVersionResponse, status_code=201)
@limiter.limit("10/minute")
async def create_rule_version(
    request: Request,
    payload: CreateVersionRequest,
    admin_data: FirebaseTokenData = Depends(require_admin),
    service: RuleVersionService = Depends(get_rule_version_service),
) -> CreateVersionResponse:
    """Create a new draft rule version with empty rules (admin only)."""
    try:
        new_version = await service.publish_version(
            version=payload.version,
            rules_json=[],
            published_by=admin_data["user_id"],
            notes="draft",
            status="draft",
        )
        return CreateVersionResponse(version=new_version.version, status=new_version.status.value)
    except InvalidVersionFormatError as e:
        raise HTTPException(status_code=400, detail=f"Invalid version format: {e}") from e
    except VersionAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=f"Version conflict: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create version: {e!s}") from e


@router.put("/rules/{version}/rules/{rule_id}", status_code=200)
@limiter.limit("30/minute")
async def edit_rule(
    version: str,
    rule_id: str,
    request: Request,
    payload: EditRuleRequest,
    admin_data: FirebaseTokenData = Depends(require_admin),
    service: RuleVersionService = Depends(get_rule_version_service),
) -> dict[str, str]:
    """Edit a rule in a version by re-publishing with updated rule data (admin only)."""
    try:
        rule_version = await service.get_by_version(version)
        if not rule_version:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")

        # Build updated rules list — replace matching rule or raise 404
        rules_json = []
        found = False
        for r in rule_version.rules:
            if r.id == rule_id:
                found = True
                rules_json.append(
                    {
                        "id": r.id,
                        "languages": payload.languages,
                        "message": payload.message,
                        "severity": payload.severity,
                        "metadata": r.metadata,
                        "patterns": [{"pattern": payload.pattern}],
                    }
                )
            else:
                rules_json.append(
                    {
                        "id": r.id,
                        "languages": r.languages,
                        "message": r.message,
                        "severity": r.severity,
                        "metadata": r.metadata,
                        "patterns": r.patterns,
                    }
                )

        if not found:
            raise HTTPException(
                status_code=404, detail=f"Rule {rule_id} not found in version {version}"
            )

        await service.update_rules(version, rules_json)
        return {"message": f"Rule {rule_id} updated in version {version}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit rule: {e!s}") from e


@router.get("/admin/metrics", status_code=200)
@limiter.limit("30/minute")
async def get_admin_metrics(
    request: Request,
    admin_data: FirebaseTokenData = Depends(require_admin),
    scan_service: ScanService = Depends(get_scan_service),
) -> dict[str, object]:
    """Global adoption metrics — active repos, scans by week, top languages (admin only)."""
    try:
        return await scan_service.get_global_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {e!s}") from e
