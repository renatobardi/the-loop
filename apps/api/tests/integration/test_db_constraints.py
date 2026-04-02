"""Integration tests — real DB constraints, server defaults, and cascade deletes.

Covers T009 (DB-level defaults), T010 (customers_affected CHECK), T011 (temporal ordering CHECK),
T080 (backfill SQL), and SC-004 (ON DELETE CASCADE for all 4 sub-resource tables).

Requires: DATABASE_URL env var pointing to a PostgreSQL 16 instance with all migrations applied.

Session strategy:
  - Constraint violation tests (T010, T011) create their own throw-away session because an
    IntegrityError leaves asyncpg in an unrecoverable state. Each session is closed after the
    violation; nothing is committed so the DB stays clean.
  - All other tests receive a `db_session` fixture that rolls back after the test.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.postgres.models import (
    IncidentActionItemRow,
    IncidentAttachmentRow,
    IncidentResponderRow,
    IncidentRow,
    IncidentTimelineEventRow,
)

from tests.integration.conftest import _make_session_factory

_NOW = datetime.now(UTC)


def _incident(**overrides: object) -> IncidentRow:
    defaults: dict[str, object] = {
        "id": uuid.uuid4(),
        "title": "Test incident",
        "category": "injection",
        "severity": "high",
        "anti_pattern": "Direct SQL concatenation",
        "remediation": "Use parameterized queries",
        "created_by": uuid.uuid4(),
    }
    defaults.update(overrides)
    return IncidentRow(**defaults)


# ---------------------------------------------------------------------------
# T009 — DB-level server defaults (sla_breached, slo_breached, postmortem_status)
# ---------------------------------------------------------------------------


class TestMigration002ServerDefaults:
    async def test_incident_new_columns_have_correct_server_defaults(
        self, db_session: AsyncSession
    ) -> None:
        """
        Insert via raw SQL omitting the new columns; verify the DB applies server_default.
        Tests the migration's DEFAULT declarations independently of ORM Python defaults.
        """
        incident_id = uuid.uuid4()

        await db_session.execute(
            text(
                "INSERT INTO incidents "
                "(id, title, category, severity, anti_pattern, remediation, created_by, "
                " affected_languages, tags, version, created_at, updated_at) "
                "VALUES (:id, 'default test', :cat, :sev, :ap, :rem, :cb, "
                " '[]'::jsonb, '[]'::jsonb, 1, now(), now())"
            ),
            {
                "id": incident_id,
                "cat": "injection",
                "sev": "high",
                "ap": "test",
                "rem": "fix",
                "cb": uuid.uuid4(),
            },
        )

        row = await db_session.execute(
            text(
                "SELECT sla_breached, slo_breached, postmortem_status FROM incidents WHERE id = :id"
            ),
            {"id": incident_id},
        )
        result = row.one()

        assert result.sla_breached is False
        assert result.slo_breached is False
        assert result.postmortem_status == "draft"


# ---------------------------------------------------------------------------
# T010 — customers_affected CHECK constraint (ck_incident_customers_nonneg)
# ---------------------------------------------------------------------------


class TestCustomersAffectedCheckConstraint:
    async def test_negative_customers_affected_violates_db_constraint(self) -> None:
        async with _make_session_factory()() as session:
            row = _incident(customers_affected=-1)
            session.add(row)
            with pytest.raises(IntegrityError, match="ck_incident_customers_nonneg"):
                await session.flush()

    async def test_zero_customers_affected_accepted(self, db_session: AsyncSession) -> None:
        row = _incident(customers_affected=0)
        db_session.add(row)
        await db_session.flush()
        await db_session.refresh(row)
        assert row.customers_affected == 0

    async def test_positive_customers_affected_accepted(self, db_session: AsyncSession) -> None:
        row = _incident(customers_affected=500)
        db_session.add(row)
        await db_session.flush()
        await db_session.refresh(row)
        assert row.customers_affected == 500


# ---------------------------------------------------------------------------
# T011 — Temporal ordering CHECK constraints
# ---------------------------------------------------------------------------


class TestTemporalOrderingConstraint:
    async def test_detected_before_started_violates_constraint(self) -> None:
        async with _make_session_factory()() as session:
            row = _incident(started_at=_NOW, detected_at=_NOW - timedelta(minutes=1))
            session.add(row)
            with pytest.raises(IntegrityError, match="ck_incident_detect_after_start"):
                await session.flush()

    async def test_detected_after_started_accepted(self, db_session: AsyncSession) -> None:
        row = _incident(started_at=_NOW, detected_at=_NOW + timedelta(minutes=5))
        db_session.add(row)
        await db_session.flush()
        await db_session.refresh(row)
        assert row.detected_at is not None

    async def test_resolved_before_ended_violates_constraint(self) -> None:
        async with _make_session_factory()() as session:
            row = _incident(ended_at=_NOW, resolved_at=_NOW - timedelta(minutes=1))
            session.add(row)
            with pytest.raises(IntegrityError, match="ck_incident_end_before_resolve"):
                await session.flush()

    async def test_resolved_after_ended_accepted(self, db_session: AsyncSession) -> None:
        row = _incident(ended_at=_NOW, resolved_at=_NOW + timedelta(minutes=5))
        db_session.add(row)
        await db_session.flush()
        await db_session.refresh(row)
        assert row.resolved_at is not None


# ---------------------------------------------------------------------------
# T080 — Backfill SQL logic against real DB
# ---------------------------------------------------------------------------


class TestBackfillStartedAt:
    async def test_backfill_sets_started_at_from_date_column(
        self, db_session: AsyncSession
    ) -> None:
        """UPDATE ... SET started_at = CAST(date AS TIMESTAMPTZ) when date is set."""
        incident_id = uuid.uuid4()
        await db_session.execute(
            text(
                "INSERT INTO incidents "
                "(id, title, category, severity, anti_pattern, remediation, created_by, "
                " date, affected_languages, tags, version, created_at, updated_at) "
                "VALUES (:id, 'backfill test', 'injection', 'high', 'ap', 'rem', :cb, "
                " '2024-06-15', '[]'::jsonb, '[]'::jsonb, 1, now(), now())"
            ),
            {"id": incident_id, "cb": uuid.uuid4()},
        )

        await db_session.execute(
            text(
                "UPDATE incidents SET started_at = CAST(date AS TIMESTAMPTZ) "
                "WHERE started_at IS NULL AND date IS NOT NULL AND id = :id"
            ),
            {"id": incident_id},
        )

        result = await db_session.execute(
            text("SELECT started_at FROM incidents WHERE id = :id"), {"id": incident_id}
        )
        started_at = result.scalar_one()
        assert started_at is not None
        assert started_at.year == 2024
        assert started_at.month == 6
        assert started_at.day == 15

    async def test_backfill_fallback_to_created_at_when_no_date(
        self, db_session: AsyncSession
    ) -> None:
        """UPDATE ... SET started_at = created_at when date IS NULL."""
        incident_id = uuid.uuid4()
        created_at_val = datetime(2024, 7, 1, 12, 0, tzinfo=UTC)
        await db_session.execute(
            text(
                "INSERT INTO incidents "
                "(id, title, category, severity, anti_pattern, remediation, created_by, "
                " affected_languages, tags, version, created_at, updated_at) "
                "VALUES (:id, 'backfill fallback', 'injection', 'high', 'ap', 'rem', :cb, "
                " '[]'::jsonb, '[]'::jsonb, 1, :ca, now())"
            ),
            {"id": incident_id, "cb": uuid.uuid4(), "ca": created_at_val},
        )

        await db_session.execute(
            text(
                "UPDATE incidents SET started_at = created_at AT TIME ZONE 'UTC' "
                "WHERE started_at IS NULL AND date IS NULL AND id = :id"
            ),
            {"id": incident_id},
        )

        result = await db_session.execute(
            text("SELECT started_at FROM incidents WHERE id = :id"), {"id": incident_id}
        )
        started_at = result.scalar_one()
        assert started_at is not None
        assert started_at.replace(tzinfo=UTC) == created_at_val

    async def test_backfill_is_idempotent(self, db_session: AsyncSession) -> None:
        """Running backfill twice must not overwrite an already-set started_at."""
        incident_id = uuid.uuid4()
        original_started_at = datetime(2024, 5, 10, tzinfo=UTC)
        await db_session.execute(
            text(
                "INSERT INTO incidents "
                "(id, title, category, severity, anti_pattern, remediation, created_by, "
                " started_at, affected_languages, tags, version, created_at, updated_at) "
                "VALUES (:id, 'idempotent test', 'injection', 'high', 'ap', 'rem', :cb, "
                " :sa, '[]'::jsonb, '[]'::jsonb, 1, now(), now())"
            ),
            {"id": incident_id, "cb": uuid.uuid4(), "sa": original_started_at},
        )

        # Run backfill — must skip rows where started_at IS NOT NULL
        await db_session.execute(
            text(
                "UPDATE incidents SET started_at = created_at AT TIME ZONE 'UTC' "
                "WHERE started_at IS NULL AND id = :id"
            ),
            {"id": incident_id},
        )

        result = await db_session.execute(
            text("SELECT started_at FROM incidents WHERE id = :id"), {"id": incident_id}
        )
        started_at = result.scalar_one()
        assert started_at.replace(tzinfo=UTC) == original_started_at


# ---------------------------------------------------------------------------
# SC-004 — ON DELETE CASCADE for all 4 sub-resource tables
# ---------------------------------------------------------------------------


class TestCascadeDeletes:
    async def _insert_incident(self, db_session: AsyncSession) -> uuid.UUID:
        row = _incident()
        db_session.add(row)
        await db_session.flush()
        return row.id

    async def test_delete_incident_cascades_to_timeline_events(
        self, db_session: AsyncSession
    ) -> None:
        incident_id = await self._insert_incident(db_session)
        event = IncidentTimelineEventRow(
            id=uuid.uuid4(),
            incident_id=incident_id,
            event_type="detection",
            description="Anomaly detected",
            occurred_at=_NOW,
            recorded_by=uuid.uuid4(),
        )
        db_session.add(event)
        await db_session.flush()
        event_id = event.id

        await db_session.execute(text("DELETE FROM incidents WHERE id = :id"), {"id": incident_id})
        await db_session.flush()

        result = await db_session.execute(
            text("SELECT id FROM incident_timeline_events WHERE id = :id"), {"id": event_id}
        )
        assert result.first() is None

    async def test_delete_incident_cascades_to_responders(self, db_session: AsyncSession) -> None:
        incident_id = await self._insert_incident(db_session)
        responder = IncidentResponderRow(
            id=uuid.uuid4(),
            incident_id=incident_id,
            user_id=uuid.uuid4(),
            role="technical_lead",
            joined_at=_NOW,
        )
        db_session.add(responder)
        await db_session.flush()
        responder_id = responder.id

        await db_session.execute(text("DELETE FROM incidents WHERE id = :id"), {"id": incident_id})
        await db_session.flush()

        result = await db_session.execute(
            text("SELECT id FROM incident_responders WHERE id = :id"), {"id": responder_id}
        )
        assert result.first() is None

    async def test_delete_incident_cascades_to_action_items(self, db_session: AsyncSession) -> None:
        incident_id = await self._insert_incident(db_session)
        action_item = IncidentActionItemRow(
            id=uuid.uuid4(),
            incident_id=incident_id,
            title="Fix vulnerability",
        )
        db_session.add(action_item)
        await db_session.flush()
        item_id = action_item.id

        await db_session.execute(text("DELETE FROM incidents WHERE id = :id"), {"id": incident_id})
        await db_session.flush()

        result = await db_session.execute(
            text("SELECT id FROM incident_action_items WHERE id = :id"), {"id": item_id}
        )
        assert result.first() is None

    async def test_delete_incident_cascades_to_attachments(self, db_session: AsyncSession) -> None:
        incident_id = await self._insert_incident(db_session)
        attachment = IncidentAttachmentRow(
            id=uuid.uuid4(),
            incident_id=incident_id,
            filename="postmortem.pdf",
            mime_type="application/pdf",
            file_size_bytes=1024,
            gcs_bucket="loop-prod-attachments",
            gcs_object_path="tenants/t1/incidents/i1/postmortem.pdf",
            attachment_type="postmortem_doc",
        )
        db_session.add(attachment)
        await db_session.flush()
        attachment_id = attachment.id

        await db_session.execute(text("DELETE FROM incidents WHERE id = :id"), {"id": incident_id})
        await db_session.flush()

        result = await db_session.execute(
            text("SELECT id FROM incident_attachments WHERE id = :id"), {"id": attachment_id}
        )
        assert result.first() is None
