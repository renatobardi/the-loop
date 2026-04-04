"""API routes for API key management — Phase 4 Semgrep platform."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.adapters.firebase.auth import FirebaseTokenData, get_firebase_token_data
from src.api.deps import get_api_key_service
from src.api.middleware import limiter
from src.domain.exceptions import ApiKeyNotFoundError
from src.domain.models import ApiKey
from src.domain.services import ApiKeyService

router = APIRouter(prefix="/api/v1", tags=["api-keys"])


# ─── Request / Response models ───────────────────────────────────────────────


class CreateApiKeyRequest(BaseModel):
    name: str


class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    prefix: str
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    @classmethod
    def from_domain(cls, key: ApiKey) -> "ApiKeyResponse":
        return cls(
            id=key.id,
            name=key.name,
            prefix=key.prefix,
            last_used_at=key.last_used_at,
            revoked_at=key.revoked_at,
            created_at=key.created_at,
        )


class CreateApiKeyResponse(ApiKeyResponse):
    token: str  # Shown only once at creation time


class WhitelistEntryRequest(BaseModel):
    rule_id: str


class WhitelistResponse(BaseModel):
    rule_ids: list[str]


# ─── Routes ──────────────────────────────────────────────────────────────────


@router.post(
    "/api-keys",
    response_model=CreateApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def create_api_key(
    request: Request,
    payload: CreateApiKeyRequest,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ApiKeyService = Depends(get_api_key_service),
) -> CreateApiKeyResponse:
    """Create a new API key for the authenticated user.

    The raw token is returned only once in the response — store it securely.
    """
    owner_id = token_data["user_id"]
    raw_token, api_key = await service.create(owner_id=owner_id, name=payload.name)
    return CreateApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        prefix=api_key.prefix,
        last_used_at=api_key.last_used_at,
        revoked_at=api_key.revoked_at,
        created_at=api_key.created_at,
        token=raw_token,
    )


@router.get(
    "/api-keys",
    response_model=list[ApiKeyResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def list_api_keys(
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ApiKeyService = Depends(get_api_key_service),
) -> list[ApiKeyResponse]:
    """List all API keys for the authenticated user (no token hashes exposed)."""
    owner_id = token_data["user_id"]
    keys = await service.list_by_user(owner_id=owner_id)
    return [ApiKeyResponse.from_domain(k) for k in keys]


@router.delete(
    "/api-keys/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
@limiter.limit("10/minute")
async def revoke_api_key(
    key_id: UUID,
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ApiKeyService = Depends(get_api_key_service),
) -> Response:
    """Revoke an API key. The key becomes immediately invalid."""
    owner_id = token_data["user_id"]
    try:
        await service.revoke(key_id=key_id, owner_id=owner_id)
    except ApiKeyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {key_id}",
        ) from e
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/api-keys/{key_id}/whitelist",
    response_model=WhitelistResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def get_whitelist(
    key_id: UUID,
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ApiKeyService = Depends(get_api_key_service),
) -> WhitelistResponse:
    """List all whitelisted rule IDs for the given API key."""
    # Verify ownership via list (revoke would be overkill; list implicitly confirms ownership)
    owner_id = token_data["user_id"]
    keys = await service.list_by_user(owner_id=owner_id)
    if not any(k.id == key_id for k in keys):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {key_id}",
        )
    rule_ids = await service.get_whitelist(key_id=key_id)
    return WhitelistResponse(rule_ids=rule_ids)


@router.post(
    "/api-keys/{key_id}/whitelist",
    response_model=WhitelistResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def add_to_whitelist(
    key_id: UUID,
    request: Request,
    payload: WhitelistEntryRequest,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ApiKeyService = Depends(get_api_key_service),
) -> WhitelistResponse:
    """Add a rule ID to the whitelist for the given API key."""
    owner_id = token_data["user_id"]
    keys = await service.list_by_user(owner_id=owner_id)
    if not any(k.id == key_id for k in keys):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {key_id}",
        )
    await service.add_to_whitelist(key_id=key_id, rule_id=payload.rule_id)
    rule_ids = await service.get_whitelist(key_id=key_id)
    return WhitelistResponse(rule_ids=rule_ids)


@router.delete(
    "/api-keys/{key_id}/whitelist/{rule_id}",
    response_model=WhitelistResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("60/minute")
async def remove_from_whitelist(
    key_id: UUID,
    rule_id: str,
    request: Request,
    token_data: FirebaseTokenData = Depends(get_firebase_token_data),
    service: ApiKeyService = Depends(get_api_key_service),
) -> WhitelistResponse:
    """Remove a rule ID from the whitelist for the given API key."""
    owner_id = token_data["user_id"]
    keys = await service.list_by_user(owner_id=owner_id)
    if not any(k.id == key_id for k in keys):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {key_id}",
        )
    await service.remove_from_whitelist(key_id=key_id, rule_id=rule_id)
    rule_ids = await service.get_whitelist(key_id=key_id)
    return WhitelistResponse(rule_ids=rule_ids)
