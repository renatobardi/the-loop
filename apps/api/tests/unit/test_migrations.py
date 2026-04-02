"""Regression tests for migration 002 constraints and backfill logic."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest
from src.domain.models import Category, Incident, PostmortemStatus, Severity


def _make_incident(**overrides: object) -> Incident:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "title": "Test incident",
        "category": Category.INJECTION,
        "severity": Severity.HIGH,
        "anti_pattern": "Direct SQL concatenation",
        "remediation": "Use parameterized queries",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": uuid4(),
    }
    defaults.update(overrides)
    return Incident(**defaults)  # type: ignore[arg-type]


class TestMigration002Defaults:
    def test_postmortem_status_defaults_to_draft(self) -> None:
        incident = _make_incident()
        assert incident.postmortem_status == PostmortemStatus.DRAFT

    def test_sla_breached_defaults_false(self) -> None:
        incident = _make_incident()
        assert incident.sla_breached is False

    def test_slo_breached_defaults_false(self) -> None:
        incident = _make_incident()
        assert incident.slo_breached is False

    def test_all_new_timestamp_fields_default_none(self) -> None:
        incident = _make_incident()
        assert incident.started_at is None
        assert incident.detected_at is None
        assert incident.ended_at is None
        assert incident.resolved_at is None

    def test_operational_fields_default_none(self) -> None:
        incident = _make_incident()
        assert incident.impact_summary is None
        assert incident.customers_affected is None
        assert incident.incident_lead_id is None
        assert incident.slack_channel_id is None
        assert incident.external_tracking_id is None


class TestMigration002CustomersAffectedConstraint:
    def test_customers_affected_zero_allowed(self) -> None:
        incident = _make_incident(customers_affected=0)
        assert incident.customers_affected == 0

    def test_customers_affected_positive_allowed(self) -> None:
        incident = _make_incident(customers_affected=500)
        assert incident.customers_affected == 500

    def test_customers_affected_negative_rejected(self) -> None:
        with pytest.raises(ValueError, match=">= 0"):
            _make_incident(customers_affected=-1)

    def test_customers_affected_none_allowed(self) -> None:
        incident = _make_incident(customers_affected=None)
        assert incident.customers_affected is None


class TestMigration002TemporalOrderingConstraint:
    def test_detect_after_start_valid(self) -> None:
        now = datetime.now(UTC)
        incident = _make_incident(
            started_at=now,
            detected_at=now + timedelta(minutes=5),
        )
        assert incident.detected_at > incident.started_at  # type: ignore[operator]

    def test_detect_before_start_rejected(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValueError, match="detected_at"):
            _make_incident(
                started_at=now,
                detected_at=now - timedelta(minutes=1),
            )

    def test_resolve_after_end_valid(self) -> None:
        now = datetime.now(UTC)
        incident = _make_incident(
            ended_at=now,
            resolved_at=now + timedelta(minutes=5),
        )
        assert incident.resolved_at > incident.ended_at  # type: ignore[operator]

    def test_resolve_before_end_rejected(self) -> None:
        now = datetime.now(UTC)
        with pytest.raises(ValueError, match="resolved_at"):
            _make_incident(
                ended_at=now,
                resolved_at=now - timedelta(minutes=1),
            )

    def test_equal_timestamps_allowed(self) -> None:
        now = datetime.now(UTC)
        incident = _make_incident(started_at=now, detected_at=now)
        assert incident.started_at == incident.detected_at

    def test_independent_pairs_not_cross_validated(self) -> None:
        now = datetime.now(UTC)
        # detected_at before ended_at is fine — no constraint between them
        incident = _make_incident(
            started_at=now,
            detected_at=now + timedelta(minutes=1),
            ended_at=now + timedelta(minutes=10),
            resolved_at=now + timedelta(minutes=15),
        )
        assert incident.started_at is not None


class TestBackfillStartedAt:
    """Test backfill logic: started_at populated from date or created_at."""

    def test_backfill_priority_date_over_created_at(self) -> None:
        incident_date = date(2024, 6, 15)
        created_at = datetime(2024, 7, 1, tzinfo=UTC)
        incident = _make_incident(date=incident_date, created_at=created_at)
        # Simulate backfill: priority 1 = use date
        expected_started_at = datetime(2024, 6, 15, tzinfo=UTC)
        simulated_started_at = (
            datetime.combine(incident.date, datetime.min.time()).replace(tzinfo=UTC)
            if incident.date
            else incident.created_at
        )
        assert simulated_started_at == expected_started_at

    def test_backfill_fallback_to_created_at_when_no_date(self) -> None:
        created_at = datetime(2024, 7, 1, 12, 0, tzinfo=UTC)
        incident = _make_incident(date=None, created_at=created_at)
        # Simulate backfill: priority 2 = use created_at when date is NULL
        simulated_started_at = incident.date or incident.created_at
        assert simulated_started_at == created_at

    def test_backfill_skips_already_set_started_at(self) -> None:
        now = datetime.now(UTC)
        incident = _make_incident(
            started_at=now,
            date=date(2024, 6, 15),
        )
        # Backfill is idempotent: if started_at already set, no change needed
        assert incident.started_at == now
