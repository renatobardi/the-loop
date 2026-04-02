"""Add operational timestamps and metadata fields to incidents.

Revision ID: 002
Revises: 001
Create Date: 2026-04-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Timestamps
    op.add_column("incidents", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidents", sa.Column("detected_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidents", sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("incidents", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))

    # Operational metadata
    op.add_column("incidents", sa.Column("impact_summary", sa.Text, nullable=True))
    op.add_column("incidents", sa.Column("customers_affected", sa.Integer, nullable=True))
    op.add_column(
        "incidents",
        sa.Column("sla_breached", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "incidents",
        sa.Column("slo_breached", sa.Boolean, nullable=False, server_default="false"),
    )
    op.add_column(
        "incidents",
        sa.Column("postmortem_status", sa.String(50), nullable=False, server_default="draft"),
    )
    op.add_column(
        "incidents",
        sa.Column("postmortem_published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("incidents", sa.Column("postmortem_due_date", sa.Date, nullable=True))
    op.add_column("incidents", sa.Column("lessons_learned", sa.Text, nullable=True))
    op.add_column("incidents", sa.Column("why_we_were_surprised", sa.Text, nullable=True))
    op.add_column("incidents", sa.Column("detection_method", sa.String(50), nullable=True))
    op.add_column("incidents", sa.Column("slack_channel_id", sa.String(50), nullable=True))
    op.add_column("incidents", sa.Column("external_tracking_id", sa.String(255), nullable=True))
    op.add_column("incidents", sa.Column("incident_lead_id", UUID, nullable=True))

    # CHECK constraints
    op.create_check_constraint(
        "ck_incident_detect_after_start",
        "incidents",
        "started_at IS NULL OR detected_at IS NULL OR started_at <= detected_at",
    )
    op.create_check_constraint(
        "ck_incident_end_before_resolve",
        "incidents",
        "ended_at IS NULL OR resolved_at IS NULL OR ended_at <= resolved_at",
    )
    op.create_check_constraint(
        "ck_incident_customers_nonneg",
        "incidents",
        "customers_affected IS NULL OR customers_affected >= 0",
    )

    # Indexes
    op.create_index("ix_incidents_started_at", "incidents", ["started_at"])
    op.create_index("ix_incidents_detected_at", "incidents", ["detected_at"])


def downgrade() -> None:
    op.drop_index("ix_incidents_detected_at", table_name="incidents")
    op.drop_index("ix_incidents_started_at", table_name="incidents")

    op.drop_constraint("ck_incident_customers_nonneg", "incidents", type_="check")
    op.drop_constraint("ck_incident_end_before_resolve", "incidents", type_="check")
    op.drop_constraint("ck_incident_detect_after_start", "incidents", type_="check")

    op.drop_column("incidents", "incident_lead_id")
    op.drop_column("incidents", "external_tracking_id")
    op.drop_column("incidents", "slack_channel_id")
    op.drop_column("incidents", "detection_method")
    op.drop_column("incidents", "why_we_were_surprised")
    op.drop_column("incidents", "lessons_learned")
    op.drop_column("incidents", "postmortem_due_date")
    op.drop_column("incidents", "postmortem_published_at")
    op.drop_column("incidents", "postmortem_status")
    op.drop_column("incidents", "slo_breached")
    op.drop_column("incidents", "sla_breached")
    op.drop_column("incidents", "customers_affected")
    op.drop_column("incidents", "impact_summary")
    op.drop_column("incidents", "resolved_at")
    op.drop_column("incidents", "ended_at")
    op.drop_column("incidents", "detected_at")
    op.drop_column("incidents", "started_at")
