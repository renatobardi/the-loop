"""Firebase Auth dependency — verifies Bearer token, extracts user UID."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials

from src.config import settings

_app: firebase_admin.App | None = None
_bearer_scheme = HTTPBearer()


def init_firebase() -> None:
    global _app  # noqa: PLW0603
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


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UUID:
    decoded = verify_token(creds.credentials)
    uid = decoded.get("uid", "")
    try:
        return UUID(uid)
    except ValueError:
        return UUID(int=hash(uid) % (2**128))
