"""Firebase Auth dependency — verifies Bearer token, extracts user UID."""

from __future__ import annotations

import json
import uuid
from typing import Any, TypedDict
from uuid import UUID

import firebase_admin  # type: ignore[import-untyped]
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from src.config import settings

_app: firebase_admin.App | None = None
_bearer_scheme = HTTPBearer()


class FirebaseTokenData(TypedDict):
    user_id: UUID
    firebase_uid: str
    email: str
    display_name: str | None


def init_firebase() -> None:
    global _app  # singleton — initialized once at lifespan startup
    if _app is not None:
        return
    if settings.firebase_service_account:
        cred = credentials.Certificate(json.loads(settings.firebase_service_account))
        _app = firebase_admin.initialize_app(cred)
    else:
        _app = firebase_admin.initialize_app()


def verify_token(token: str) -> dict[str, Any]:
    try:
        return auth.verify_id_token(token)  # type: ignore[no-any-return]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        ) from e


def _uid_to_uuid(uid: str) -> UUID:
    """Convert Firebase UID to deterministic UUID (uuid5 for non-UUID UIDs)."""
    try:
        return UUID(uid)
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"firebase:{uid}")


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    """Return deterministic UUID for the authenticated Firebase user."""
    decoded = verify_token(creds.credentials)
    return _uid_to_uuid(decoded.get("uid", ""))


async def get_firebase_token_data(
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> FirebaseTokenData:
    """Return full token data: user_id, firebase_uid, email, display_name."""
    decoded = verify_token(creds.credentials)
    uid: str = decoded.get("uid", "")
    return FirebaseTokenData(
        user_id=_uid_to_uuid(uid),
        firebase_uid=uid,
        email=decoded.get("email", ""),
        display_name=decoded.get("name") or None,
    )
