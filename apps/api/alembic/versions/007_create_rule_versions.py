"""Create rule_versions table for Phase B API integration.

Revision ID: 007
Revises: 006
Create Date: 2026-04-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create rule_versions table with constraints and indexes."""
    op.create_table(
        "rule_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.func.gen_random_uuid()),
        sa.Column("version", sa.String(20), nullable=False, unique=True),
        sa.Column("rules_json", JSONB, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("published_by", UUID(as_uuid=True), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),

        # Constraints
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'deprecated')",
            name="status_check",
        ),
        sa.CheckConstraint(
            "(status = 'deprecated' AND deprecated_at IS NOT NULL) OR (status != 'deprecated' AND deprecated_at IS NULL)",
            name="valid_deprecation",
        ),
        sa.CheckConstraint(
            "version ~ '^[0-9]+\\.[0-9]+\\.[0-9]+$'",
            name="version_format",
        ),
    )

    # Create indexes
    op.create_index(
        "idx_rule_versions_status",
        "rule_versions",
        ["status"],
    )
    op.create_index(
        "idx_rule_versions_version",
        "rule_versions",
        ["version"],
    )
    op.create_index(
        "idx_rule_versions_created_at",
        "rule_versions",
        ["created_at"],
        postgresql_using="btree",
    )


def downgrade() -> None:
    """Drop rule_versions table and indexes."""
    op.drop_index("idx_rule_versions_created_at", table_name="rule_versions")
    op.drop_index("idx_rule_versions_version", table_name="rule_versions")
    op.drop_index("idx_rule_versions_status", table_name="rule_versions")
    op.drop_table("rule_versions")
