"""Unit tests for IncidentResponder domain model."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from src.domain.models import IncidentResponder, ResponderRole


def _make_responder(**overrides: object) -> IncidentResponder:
    now = datetime.now(timezone.utc)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "incident_id": uuid4(),
        "user_id": uuid4(),
        "role": ResponderRole.TECHNICAL_LEAD,
        "joined_at": now,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return IncidentResponder(**defaults)  # type: ignore[arg-type]


def test_create_responder() -> None:
    r = _make_responder()
    assert r.role == ResponderRole.TECHNICAL_LEAD
    assert r.left_at is None
    assert r.contribution_summary is None


def test_left_before_joined_rejected() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="left_at"):
        _make_responder(joined_at=now, left_at=now - timedelta(hours=1))


def test_left_at_equal_joined_at_allowed() -> None:
    now = datetime.now(timezone.utc)
    r = _make_responder(joined_at=now, left_at=now)
    assert r.left_at == r.joined_at


def test_all_roles_accepted() -> None:
    for role in ResponderRole:
        r = _make_responder(role=role)
        assert r.role == role
