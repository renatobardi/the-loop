"""Create incident_timeline_events table.

Revision ID: 004
Revises: 003
Create Date: 2026-04-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incident_timeline_events",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", UUID, nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_by", UUID, nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("external_reference_url", sa.String(2048), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incidents.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index("ix_timeline_events_incident_id", "incident_timeline_events", ["incident_id"])
    op.create_index("ix_timeline_events_occurred_at", "incident_timeline_events", ["occurred_at"])
    op.create_index(
        "ix_timeline_events_incident_occurred",
        "incident_timeline_events",
        ["incident_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_timeline_events_incident_occurred", table_name="incident_timeline_events")
    op.drop_index("ix_timeline_events_occurred_at", table_name="incident_timeline_events")
    op.drop_index("ix_timeline_events_incident_id", table_name="incident_timeline_events")
    op.drop_table("incident_timeline_events")
