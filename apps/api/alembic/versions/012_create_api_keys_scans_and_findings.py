"""create api_keys, scans, and scan_findings tables

Revision ID: 012
Revises: 011
Create Date: 2026-04-04
"""

import sqlalchemy as sa
from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("prefix", sa.String(10), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name="fk_api_keys_owner_id"),
        sa.UniqueConstraint("key_hash", name="uq_api_keys_key_hash"),
    )
    op.create_index("idx_api_keys_owner_id", "api_keys", ["owner_id"])

    op.create_table(
        "scans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("api_key_id", sa.UUID(), nullable=False),
        sa.Column("repository", sa.String(255), nullable=False),
        sa.Column("branch", sa.String(255), nullable=False),
        sa.Column("pr_number", sa.Integer(), nullable=True),
        sa.Column("rules_version", sa.String(20), nullable=False),
        sa.Column("findings_count", sa.Integer(), nullable=False),
        sa.Column("errors_count", sa.Integer(), nullable=False),
        sa.Column("warnings_count", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"], name="fk_scans_api_key_id"),
    )
    op.create_index("idx_scans_api_key_id", "scans", ["api_key_id"])
    op.create_index("idx_scans_created_at", "scans", ["created_at"])

    op.create_table(
        "scan_findings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scan_id", sa.UUID(), nullable=False),
        sa.Column("rule_id", sa.String(100), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], name="fk_scan_findings_scan_id"),
    )
    op.create_index("idx_scan_findings_scan_id", "scan_findings", ["scan_id"])
    op.create_index("idx_scan_findings_rule_id", "scan_findings", ["rule_id"])


def downgrade() -> None:
    op.drop_index("idx_scan_findings_rule_id", table_name="scan_findings")
    op.drop_index("idx_scan_findings_scan_id", table_name="scan_findings")
    op.drop_table("scan_findings")

    op.drop_index("idx_scans_created_at", table_name="scans")
    op.drop_index("idx_scans_api_key_id", table_name="scans")
    op.drop_table("scans")

    op.drop_index("idx_api_keys_owner_id", table_name="api_keys")
    op.drop_table("api_keys")
