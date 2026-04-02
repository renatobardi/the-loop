"""Unit tests for IncidentActionItem domain model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from src.domain.models import ActionItemPriority, ActionItemStatus, IncidentActionItem


def _make_item(**overrides: object) -> IncidentActionItem:
    now = datetime.now(UTC)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "incident_id": uuid4(),
        "title": "Fix the bug",
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return IncidentActionItem(**defaults)  # type: ignore[arg-type]


def test_create_action_item_defaults_status_open() -> None:
    item = _make_item()
    assert item.status == ActionItemStatus.OPEN
    assert item.priority == ActionItemPriority.MEDIUM
    assert item.completed_at is None
    assert item.due_date is None


def test_empty_title_rejected() -> None:
    with pytest.raises(ValueError, match="empty"):
        _make_item(title="   ")


def test_frozen_model() -> None:
    item = _make_item()
    with pytest.raises(Exception):
        item.title = "changed"  # type: ignore[misc]
