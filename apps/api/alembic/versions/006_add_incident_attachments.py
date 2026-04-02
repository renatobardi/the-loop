"""Create incident_attachments table.

Revision ID: 006
Revises: 005
Create Date: 2026-04-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "incident_attachments",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", UUID, nullable=False),
        sa.Column("uploaded_by", UUID, nullable=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=False),
        sa.Column("gcs_bucket", sa.String(255), nullable=False),
        sa.Column("gcs_object_path", sa.String(1000), nullable=False),
        sa.Column("content_text", sa.Text, nullable=True),
        sa.Column(
            "extraction_status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("attachment_type", sa.String(50), nullable=False),
        sa.Column("source_system", sa.String(100), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
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
            "file_size_bytes > 0",
            name="ck_attachment_file_size_positive",
        ),
    )

    op.create_index("ix_attachments_incident_id", "incident_attachments", ["incident_id"])


def downgrade() -> None:
    op.drop_index("ix_attachments_incident_id", table_name="incident_attachments")
    op.drop_table("incident_attachments")
