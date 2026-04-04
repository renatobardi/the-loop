"""create rule_whitelists table

Revision ID: 013
Revises: 012
Create Date: 2026-04-04
"""

import sqlalchemy as sa
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rule_whitelists",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("api_key_id", sa.UUID(), nullable=False),
        sa.Column("rule_id", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["api_key_id"], ["api_keys.id"], name="fk_rule_whitelists_api_key_id"
        ),
        sa.UniqueConstraint("api_key_id", "rule_id", name="uq_rule_whitelists_key_rule"),
    )
    op.create_index("idx_rule_whitelists_api_key_id", "rule_whitelists", ["api_key_id"])


def downgrade() -> None:
    op.drop_index("idx_rule_whitelists_api_key_id", table_name="rule_whitelists")
    op.drop_table("rule_whitelists")
