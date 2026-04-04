"""Port interface for user profile persistence."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.models import User


class UserRepoPort(Protocol):
    async def get_or_create(
        self, firebase_uid: str, email: str, display_name: str | None
    ) -> User: ...

    async def update(
        self, user_id: UUID, display_name: str | None, job_title: str | None
    ) -> User: ...
