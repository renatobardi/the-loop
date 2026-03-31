"""Create incidents table with pgvector and pg_trgm extensions.

Revision ID: 001
Create Date: 2026-03-31
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "incidents",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("date", sa.Date, nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("organization", sa.String(255), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("failure_mode", sa.Text, nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("affected_languages", JSONB, nullable=False, server_default="[]"),
        sa.Column("anti_pattern", sa.Text, nullable=False),
        sa.Column("code_example", sa.Text, nullable=True),
        sa.Column("remediation", sa.Text, nullable=False),
        sa.Column("static_rule_possible", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("semgrep_rule_id", sa.String(50), nullable=True),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("tags", JSONB, nullable=False, server_default="[]"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.Column("created_by", UUID, nullable=False),
    )

    op.create_index("ix_incidents_created_at", "incidents", [sa.text("created_at DESC")])
    op.create_index("ix_incidents_category", "incidents", ["category"])
    op.create_index("ix_incidents_severity", "incidents", ["severity"])

    op.execute(
        "CREATE UNIQUE INDEX uq_incidents_source_url ON incidents (source_url) "
        "WHERE deleted_at IS NULL AND source_url IS NOT NULL"
    )

    op.execute(
        "CREATE INDEX ix_incidents_keyword_search ON incidents "
        "USING gin ((title || ' ' || anti_pattern || ' ' || remediation) gin_trgm_ops)"
    )


def downgrade() -> None:
    op.drop_table("incidents")
