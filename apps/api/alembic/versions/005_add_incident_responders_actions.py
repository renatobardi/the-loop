"""Create incident_responders and incident_action_items tables.

Revision ID: 005
Revises: 004
Create Date: 2026-04-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incident_responders",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", UUID, nullable=False),
        sa.Column("user_id", UUID, nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("contribution_summary", sa.Text, nullable=True),
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
        sa.UniqueConstraint("incident_id", "user_id", name="uq_responder_incident_user"),
        sa.CheckConstraint(
            "left_at IS NULL OR joined_at <= left_at",
            name="ck_responder_left_after_joined",
        ),
    )

    op.create_index("ix_responders_incident_id", "incident_responders", ["incident_id"])
    op.create_index("ix_responders_user_id", "incident_responders", ["user_id"])

    op.create_table(
        "incident_action_items",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", UUID, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("owner_id", UUID, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by", UUID, nullable=True),
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
        sa.CheckConstraint(
            "char_length(title) > 0",
            name="ck_action_item_title_nonempty",
        ),
    )

    op.create_index("ix_action_items_incident_id", "incident_action_items", ["incident_id"])
    op.create_index("ix_action_items_owner_id", "incident_action_items", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_action_items_owner_id", table_name="incident_action_items")
    op.drop_index("ix_action_items_incident_id", table_name="incident_action_items")
    op.drop_table("incident_action_items")

    op.drop_index("ix_responders_user_id", table_name="incident_responders")
    op.drop_index("ix_responders_incident_id", table_name="incident_responders")
    op.drop_table("incident_responders")
