"""Unit tests for domain models — validation, enums, boundaries."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from src.domain.models import Category, DetectionMethod, Incident, PostmortemStatus, Severity


def _make_incident(**overrides: object) -> Incident:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "title": "Test incident",
        "category": Category.INJECTION,
        "severity": Severity.HIGH,
        "anti_pattern": "Direct SQL concatenation",
        "remediation": "Use parameterized queries",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": uuid4(),
    }
    defaults.update(overrides)
    return Incident(**defaults)  # type: ignore[arg-type]


class TestCategory:
    def test_all_12_values(self) -> None:
        assert len(Category) == 12

    def test_values_are_kebab_case(self) -> None:
        for cat in Category:
            assert cat.value == cat.value.lower()
            assert " " not in cat.value


class TestSeverity:
    def test_all_4_values(self) -> None:
        assert len(Severity) == 4

    def test_ordering(self) -> None:
        values = [s.value for s in Severity]
        assert values == ["critical", "high", "medium", "low"]


class TestIncident:
    def test_valid_creation(self) -> None:
        incident = _make_incident()
        assert incident.version == 1
        assert incident.deleted_at is None
        assert incident.embedding is None

    def test_frozen(self) -> None:
        incident = _make_incident()
        with pytest.raises(Exception):
            incident.title = "Changed"  # type: ignore[misc]

    def test_title_max_500(self) -> None:
        _make_incident(title="a" * 500)

    def test_title_501_rejected(self) -> None:
        with pytest.raises(ValueError, match="500 characters"):
            _make_incident(title="a" * 501)

    def test_title_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="1 and 500"):
            _make_incident(title="   ")

    def test_anti_pattern_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="not be empty"):
            _make_incident(anti_pattern="   ")

    def test_remediation_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="not be empty"):
            _make_incident(remediation="")

    def test_source_url_max_2048(self) -> None:
        _make_incident(source_url="https://example.com/" + "a" * 2020)

    def test_source_url_over_2048_rejected(self) -> None:
        with pytest.raises(ValueError, match="2048"):
            _make_incident(source_url="https://example.com/" + "a" * 2040)

    def test_source_url_empty_becomes_none(self) -> None:
        incident = _make_incident(source_url="   ")
        assert incident.source_url is None

    def test_semgrep_rule_id_valid(self) -> None:
        _make_incident(semgrep_rule_id="injection-001")

    def test_semgrep_rule_id_invalid_format(self) -> None:
        with pytest.raises(ValueError, match="format"):
            _make_incident(semgrep_rule_id="bad_format")

    def test_semgrep_rule_id_too_long(self) -> None:
        with pytest.raises(ValueError, match="50 characters"):
            _make_incident(semgrep_rule_id="a" * 51)

    def test_embedding_must_be_null(self) -> None:
        with pytest.raises(ValueError, match="NULL in Phase A"):
            _make_incident(embedding=[0.1] * 768)

    def test_version_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match=">= 1"):
            _make_incident(version=0)

    def test_tags_filters_empty_strings(self) -> None:
        incident = _make_incident(tags=["valid", "", "  ", "also-valid"])
        assert incident.tags == ["valid", "also-valid"]

    def test_customers_affected_negative_rejected(self) -> None:
        with pytest.raises(ValueError, match=">= 0"):
            _make_incident(customers_affected=-1)

    def test_customers_affected_zero_allowed(self) -> None:
        incident = _make_incident(customers_affected=0)
        assert incident.customers_affected == 0

    def test_postmortem_status_default_draft(self) -> None:
        incident = _make_incident()
        assert incident.postmortem_status == PostmortemStatus.DRAFT

    def test_detection_method_enum(self) -> None:
        incident = _make_incident(detection_method=DetectionMethod.MONITORING_ALERT)
        assert incident.detection_method == DetectionMethod.MONITORING_ALERT

    def test_temporal_constraint_detect_before_start_rejected(self) -> None:
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="detected_at"):
            _make_incident(
                started_at=now,
                detected_at=now - timedelta(minutes=5),
            )

    def test_temporal_constraint_end_before_resolve_rejected(self) -> None:
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="resolved_at"):
            _make_incident(
                ended_at=now,
                resolved_at=now - timedelta(minutes=5),
            )

    def test_temporal_constraint_valid_order_accepted(self) -> None:
        now = datetime.now(timezone.utc)
        incident = _make_incident(
            started_at=now,
            detected_at=now + timedelta(minutes=2),
            ended_at=now + timedelta(minutes=10),
            resolved_at=now + timedelta(minutes=15),
        )
        assert incident.started_at == now

    def test_duration_minutes_computed(self) -> None:
        now = datetime.now(timezone.utc)
        incident = _make_incident(
            started_at=now,
            ended_at=now + timedelta(minutes=42),
        )
        assert incident.duration_minutes == 42

    def test_duration_minutes_none_when_missing_timestamps(self) -> None:
        incident = _make_incident(started_at=datetime.now(timezone.utc))
        assert incident.duration_minutes is None

    def test_time_to_detect_minutes_computed(self) -> None:
        now = datetime.now(timezone.utc)
        incident = _make_incident(
            started_at=now,
            detected_at=now + timedelta(minutes=3),
        )
        assert incident.time_to_detect_minutes == 3

    def test_time_to_resolve_minutes_computed(self) -> None:
        now = datetime.now(timezone.utc)
        incident = _make_incident(
            started_at=now,
            resolved_at=now + timedelta(minutes=120),
        )
        assert incident.time_to_resolve_minutes == 120

    def test_raw_content_and_tech_context_stored(self) -> None:
        raw = {"summary": "test", "root_cause": "bug"}
        ctx = {"languages": ["python"], "frameworks": ["fastapi"]}
        incident = _make_incident(raw_content=raw, tech_context=ctx)
        assert incident.raw_content == raw
        assert incident.tech_context == ctx
