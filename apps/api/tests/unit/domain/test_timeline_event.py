"""Unit tests for IncidentTimelineEvent domain model."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from src.domain.models import IncidentTimelineEvent, TimelineEventType


def _make_event(**overrides: object) -> IncidentTimelineEvent:
    now = datetime.now(timezone.utc)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "incident_id": uuid4(),
        "event_type": TimelineEventType.DETECTED,
        "description": "Monitoring alert triggered",
        "occurred_at": now,
        "recorded_by": uuid4(),
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return IncidentTimelineEvent(**defaults)  # type: ignore[arg-type]


def test_create_timeline_event() -> None:
    event = _make_event()
    assert event.event_type == TimelineEventType.DETECTED
    assert event.duration_minutes is None
    assert event.external_reference_url is None


def test_invalid_event_type_rejected() -> None:
    with pytest.raises(Exception):
        _make_event(event_type="not-a-valid-type")


def test_negative_duration_rejected() -> None:
    with pytest.raises(ValueError, match=">= 0"):
        _make_event(duration_minutes=-1)


def test_zero_duration_allowed() -> None:
    event = _make_event(duration_minutes=0)
    assert event.duration_minutes == 0


def test_empty_description_rejected() -> None:
    with pytest.raises(ValueError, match="not be empty"):
        _make_event(description="   ")


def test_frozen_model() -> None:
    event = _make_event()
    with pytest.raises(Exception):
        event.description = "changed"  # type: ignore[misc]


def test_all_event_types_accepted() -> None:
    for et in TimelineEventType:
        ev = _make_event(event_type=et)
        assert ev.event_type == et
