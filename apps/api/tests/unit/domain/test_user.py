"""Unit tests for User domain model, UserPlan enum, and UserNotFoundError."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from src.domain.exceptions import UserNotFoundError
from src.domain.models import User, UserPlan


def _make_user(**overrides: object) -> User:
    now = datetime.now(UTC)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "firebase_uid": "abc123firebaseuid",
        "email": "user@example.com",
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return User(**defaults)  # type: ignore[arg-type]


# ─── UserPlan enum ────────────────────────────────────────────────────────────


def test_user_plan_values() -> None:
    assert UserPlan.FREE == "free"
    assert UserPlan.BETA == "beta"
    assert UserPlan.STARTER == "starter"
    assert UserPlan.PRO == "pro"
    assert UserPlan.ENTERPRISE == "enterprise"


def test_user_plan_invalid_value_raises() -> None:
    with pytest.raises(ValueError):
        UserPlan("invalid_plan")


# ─── User model ───────────────────────────────────────────────────────────────


def test_user_defaults() -> None:
    user = _make_user()
    assert user.plan == UserPlan.BETA
    assert user.display_name is None
    assert user.job_title is None


def test_user_required_fields() -> None:
    now = datetime.now(UTC)
    with pytest.raises(Exception):
        User(id=uuid4(), created_at=now, updated_at=now)  # type: ignore[call-arg]


def test_user_frozen() -> None:
    user = _make_user()
    with pytest.raises(Exception):
        user.email = "other@example.com"  # type: ignore[misc]


def test_user_with_display_name() -> None:
    user = _make_user(display_name="Renato Bardi")
    assert user.display_name == "Renato Bardi"


def test_user_with_all_plans() -> None:
    for plan in UserPlan:
        user = _make_user(plan=plan)
        assert user.plan == plan


# ─── UserNotFoundError ────────────────────────────────────────────────────────


def test_user_not_found_error_stores_id() -> None:
    err = UserNotFoundError("some-user-id")
    assert err.user_id == "some-user-id"
    assert "some-user-id" in str(err)
